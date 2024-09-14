import cv2
from flask import Flask, Response

app = Flask(__name__)

# Función para capturar el video de la cámara y transmitirlo como un flujo MJPEG
def generate_frames():
    cap = cv2.VideoCapture(0)  # Accede a la cámara
    while True:
        success, frame = cap.read()
        if not success:
            break
        else:
            # Codificar la imagen en formato JPEG
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()

            # Usar formato de respuesta MJPEG para transmitir los frames
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    cap.release()

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001)
