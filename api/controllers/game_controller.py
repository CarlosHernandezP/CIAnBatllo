# game_controller.py
from flask import render_template,Response
from flask_socketio import SocketIO, emit
import cv2
import mediapipe as mp
import requests
import numpy as np
import time

# Crear una instancia de SocketIO fuera de la función para que esté disponible en todo el módulo
socketio = SocketIO()

def init_socketio(app):
	# Inicializar SocketIO con la aplicación Flask
	socketio.init_app(app)

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
    Conecta al stream HTTP que expone el video de la cámara y procesa los frames con MediaPipe.
    """
    # URL del stream HTTP (reemplazar <host-ip> con la IP del host donde se está ejecutando el servidor Flask)
    stream_url = 'http://192.168.1.17:5001/video_feed'
    stream = requests.get(stream_url, stream=True)

    # Inicialización de MediaPipe con parámetros optimizados
    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose(static_image_mode=False, min_detection_confidence=0.5, min_tracking_confidence=0.5)
    mp_drawing = mp.solutions.drawing_utils

    byte_data = b''
    for chunk in stream.iter_content(chunk_size=1024):
        byte_data += chunk
        a = byte_data.find(b'\xff\xd8')
        b = byte_data.find(b'\xff\xd9')

        if a != -1 and b != -1:
            jpg = byte_data[a:b+2]
            byte_data = byte_data[b+2:]

            # Decodificar la imagen JPEG
            image = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)

            # Reducir la resolución del frame para mejorar el rendimiento
            image = cv2.resize(image, (640, 480))  # Ajustar a 640x480 para reducir el procesamiento

            # Procesar la pose con MediaPipe
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results = pose.process(image_rgb)

            # Dibujar landmarks de la pose si están disponibles
            if results.pose_landmarks:
                mp_drawing.draw_landmarks(
                    image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

                # Obtener coordenadas de muñecas y hombros
                right_wrist = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_WRIST]
                left_wrist = results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_WRIST]
                right_shoulder = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_SHOULDER]
                left_shoulder = results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_SHOULDER]

                # Enviar evento personalizado cuando la mano izquierda está levantada
                if left_wrist.y < left_shoulder.y:
                    print("Left hand raised - Sending custom event")
                    socketio.emit('hand_raised_event', {'left_hand_raised': True})
                if right_wrist.y < right_shoulder.y:
                    print("Right hand raised - Sending custom event")
                    socketio.emit('hand_raised_event', {'right_hand_raised': True})

            # Voltear la imagen horizontalmente
            image = cv2.flip(image, 1)

            # Codificar la imagen en formato JPEG y reducir la calidad para ahorrar ancho de banda
            _, buffer = cv2.imencode('.jpg', image, [int(cv2.IMWRITE_JPEG_QUALITY), 70])  # Reducir calidad a 70

            frame = buffer.tobytes()

            # Limitar la tasa de frames para reducir el procesamiento
            time.sleep(0.03)  # Limitar a 30 FPS

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


    # Liberar recursos al cerrar
    cap.release()
