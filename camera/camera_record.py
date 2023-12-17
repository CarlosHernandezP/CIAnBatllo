# camera_record.py
import cv2
import mediapipe as mp

# Initialize MediaPipe Pose
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
mp_drawing = mp.solutions.drawing_utils

def update_hand_gesture(queue):
    # Initialize the webcam
    cap = cv2.VideoCapture(0)

    while cap.isOpened():
        success, image = cap.read()
        if not success:
            continue

        # Convert the color from BGR to RGB for MediaPipe processing
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = pose.process(rgb_image)

        # Convert back to BGR for displaying
        bgr_image = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2BGR)

        if results.pose_landmarks:
            # Draw landmarks for debugging
            mp_drawing.draw_landmarks(
                bgr_image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

            # Get landmarks for left wrist and shoulder
            landmarks = results.pose_landmarks.landmark
            left_wrist = landmarks[mp_pose.PoseLandmark.LEFT_WRIST]
            left_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER]

            # Check if left hand is raised
            is_raised = left_wrist.y < left_shoulder.y
            queue.put(is_raised)

           

        # Display the image with landmarks for debugging
        cv2.imshow('MediaPipe Pose', bgr_image)
        if cv2.waitKey(5) & 0xFF == 27:
            break

    cap.release()
