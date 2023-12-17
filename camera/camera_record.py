import cv2
import mediapipe as mp

# Initialize MediaPipe Pose
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
mp_drawing = mp.solutions.drawing_utils

# Initialize the webcam
cap = cv2.VideoCapture(0)

while cap.isOpened():
    success, image = cap.read()
    if not success:
        print("Ignoring empty camera frame.")
        continue

    # Convert the color from BGR to RGB and process it
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = pose.process(image)

    # Draw the pose annotations
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    if results.pose_landmarks:
        mp_drawing.draw_landmarks(
            image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

        # Get landmarks for left and right wrists
        landmarks = results.pose_landmarks.landmark
        right_wrist = landmarks[mp_pose.PoseLandmark.RIGHT_WRIST]
        left_wrist = landmarks[mp_pose.PoseLandmark.LEFT_WRIST]
        right_shoulder = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER]
        left_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER]

        # Check if hands are raised
        if right_wrist.y < right_shoulder.y:
            image[:, :, 0] = image[:, :, 0] * 0.5  # Reduce red and green channels
            image[:, :, 1] = image[:, :, 1] * 0.5

        if left_wrist.y < left_shoulder.y:
            image[:, :, 1] = image[:, :, 1] * 0.5  # Reduce green and blue channels
            image[:, :, 2] = image[:, :, 2] * 0.5

    # Display the image
    cv2.imshow('MediaPipe Pose with Color Change', image)

    if cv2.waitKey(5) & 0xFF == 27:
        break

cap.release()
