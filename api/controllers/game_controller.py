# game_controller.py
import os
import time
from typing import Dict

import cv2
from mediapipe.python.solutions import pose as mp_pose
from mediapipe.python.solutions.pose import POSE_CONNECTIONS, PoseLandmark
from mediapipe.python.solutions import drawing_utils as mp_drawing
import numpy as np
import requests
from flask import current_app, render_template, Response
from flask_socketio import SocketIO

# Crear una instancia de SocketIO fuera de la función para que esté disponible en todo el módulo
socketio = SocketIO()

# Parámetros ajustables mediante variables de entorno para facilitar la optimización
STREAM_URL = os.getenv('STREAM_URL', 'http://127.0.0.1:5001/video_feed')
FRAME_WIDTH = int(os.getenv('GAME_FRAME_WIDTH', '640'))
FRAME_HEIGHT = int(os.getenv('GAME_FRAME_HEIGHT', '480'))
TARGET_FPS = float(os.getenv('GAME_TARGET_FPS', '30'))
EVENT_COOLDOWN = float(os.getenv('HAND_EVENT_COOLDOWN', '0.3'))
STREAM_TIMEOUT = float(os.getenv('STREAM_TIMEOUT', '5'))

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

def _emit_hand_event(hand: str, payload: Dict[str, bool]) -> None:
    """Envía un evento Socket.IO y registra errores sin bloquear el loop."""
    try:
        socketio.emit('hand_raised_event', payload)
    except Exception as exc:  # pylint: disable=broad-except
        current_app.logger.error('Error emitiendo evento de mano %s: %s', hand, exc)


def generate_frames():
    """Conecta al stream de cámara, procesa MediaPipe y emite eventos con cooldown."""
    try:
        stream = requests.get(STREAM_URL, stream=True, timeout=STREAM_TIMEOUT)
        stream.raise_for_status()
    except requests.RequestException as exc:
        current_app.logger.error('No se pudo conectar al stream %s: %s', STREAM_URL, exc)
        return

    pose = mp_pose.Pose(
        static_image_mode=False,
        model_complexity=0,
        smooth_landmarks=False,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
    )

    byte_data = b''
    frame_interval = 1.0 / TARGET_FPS if TARGET_FPS > 0 else 0.0
    last_emit = {'left': 0.0, 'right': 0.0}
    last_frame_time = time.perf_counter()

    try:
        for chunk in stream.iter_content(chunk_size=2048):
            byte_data += chunk
            start = byte_data.find(b'\xff\xd8')
            end = byte_data.find(b'\xff\xd9')

            if start == -1 or end == -1:
                continue

            jpg = byte_data[start:end + 2]
            byte_data = byte_data[end + 2:]

            image = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
            if image is None:
                continue

            image = cv2.resize(image, (FRAME_WIDTH, FRAME_HEIGHT), interpolation=cv2.INTER_AREA)
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results = pose.process(image_rgb)

            if getattr(results, 'pose_landmarks', None):
                mp_drawing.draw_landmarks(
                    image,
                    results.pose_landmarks,  # type: ignore[attr-defined]
                    list(POSE_CONNECTIONS),
                )
                landmarks = results.pose_landmarks.landmark  # type: ignore[attr-defined]
                right_wrist = landmarks[PoseLandmark.RIGHT_WRIST]
                left_wrist = landmarks[PoseLandmark.LEFT_WRIST]
                right_shoulder = landmarks[PoseLandmark.RIGHT_SHOULDER]
                left_shoulder = landmarks[PoseLandmark.LEFT_SHOULDER]

                hand_states = {
                    'left': left_wrist.y < left_shoulder.y,
                    'right': right_wrist.y < right_shoulder.y,
                }
                now = time.perf_counter()
                for hand, is_up in hand_states.items():
                    if is_up and now - last_emit[hand] >= EVENT_COOLDOWN:
                        payload = {
                            'hand': hand,
                            'left_hand_raised': hand == 'left',
                            'right_hand_raised': hand == 'right',
                        }
                        _emit_hand_event(hand, payload)
                        last_emit[hand] = now

            image = cv2.flip(image, 1)
            _, buffer = cv2.imencode('.jpg', image, [int(cv2.IMWRITE_JPEG_QUALITY), 70])
            frame = buffer.tobytes()

            elapsed = time.perf_counter() - last_frame_time
            if frame_interval > 0 and elapsed < frame_interval:
                time.sleep(frame_interval - elapsed)
            last_frame_time = time.perf_counter()

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    finally:
        stream.close()
        pose.close()
