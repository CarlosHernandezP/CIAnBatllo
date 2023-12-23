# game_controller.py
from flask import render_template,Response
import cv2
import mediapipe as mp


def game():
    # Renderiza la plantilla 'index.html'
    return render_template('game.html')


def video_game():
    """
    Transmite el video en tiempo real con información de pose procesada.
    """
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

def generate_frames():
    """
    Genera los frames del video, procesando la información de la pose.
    """
    # Inicialización de objetos Mediapipe para pose y dibujo
    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose()
    mp_drawing = mp.solutions.drawing_utils

    # Inicialización de la cámara
    cap = cv2.VideoCapture(0)

    while cap.isOpened():
        # Captura del frame de la cámara
        success, image = cap.read()
        if not success:
            print("Ignoring empty camera frame.")
            continue

        # Conversión de colores para Mediapipe
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = pose.process(image)

        # Conversión de colores de vuelta para OpenCV
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        # Dibujar landmarks de la pose si están disponibles
        if results.pose_landmarks:
            mp_drawing.draw_landmarks(
                image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

            # Obtener coordenadas de muñecas y hombros
            right_wrist = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_WRIST]
            left_wrist = results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_WRIST]
            right_shoulder = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_SHOULDER]
            left_shoulder = results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_SHOULDER]

            # Aplicar efectos de color basados en posición de muñecas respecto a hombros
            if right_wrist.y < right_shoulder.y:
                image[:, :, 0] = image[:, :, 0] * 0.5
                image[:, :, 1] = image[:, :, 1] * 0.5

            if left_wrist.y < left_shoulder.y:
                image[:, :, 1] = image[:, :, 1] * 0.5
                image[:, :, 2] = image[:, :, 2] * 0.5

        # Voltear la imagen horizontalmente
        image = cv2.flip(image, 1)

        # Codificar la imagen en formato JPEG y enviarla como bytes
        _, buffer = cv2.imencode('.jpg', image)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    # Liberar recursos al cerrar
    cap.release()
