
## Download repo:
https://github.com/crowsonkb/v-diffusion-pytorch


## Model checkpoints: 
https://the-eye.eu/public/AI/models/v-diffusion/cc12m_1_cfg.pth


## These are the requirements: 
argparse
clip
k_diffusion
sounddevice
torch
wavfile
mtranslate
gtts
openai-whisper
ffmpeg-python
mediapipe
pygame
opencv-python
flask-socketio


## Excecute:
To execute the api, type flask run inside api folder

## Optimización de `game_controller`
Para reducir el retardo entre la detección de movimiento (MediaPipe) y las acciones de JavaScript en `static/js/game.js`, sigue estos pasos desde Ubuntu usando `uv`:

1. **Configura dependencias del stream**
	```bash
	sudo apt update && sudo apt install -y ffmpeg portaudio19-dev libasound2-dev libgl1
	uv pip sync requirements.txt
	```
	Esto garantiza que `MediaPipe`, `OpenCV` y `sounddevice` tengan las librerías nativas disponibles.

2. **Define el origen del video por variable de entorno** (evita hardcodear IPs en `game_controller`):
	```bash
	export STREAM_URL="http://127.0.0.1:5001/video_feed"
	```
	Luego en `api/controllers/game_controller.py` carga la variable:
	```python
	import os
	stream_url = os.getenv("STREAM_URL", "http://127.0.0.1:5001/video_feed")
	```

3. **Arranca procesos en paralelo**
	```bash
	# Terminal A
	uv run python camera_server.py

	# Terminal B
	uv run python api/app.py  # Socket.IO incluido
	```
	Comprueba que `curl $STREAM_URL` devuelve datos MJPEG antes de abrir `/game`.

4. **Ajusta MediaPipe para menor latencia**
	- Modifica el inicializador a `mp_pose.Pose(model_complexity=0, smooth_landmarks=False)`.
	- Reduce la calidad/size de los frames solo una vez antes del procesamiento.
	- Sustituye `time.sleep(0.03)` por un control basado en timestamps para no bloquear la captura.

5. **Envía eventos Socket.IO con `cooldown`**
	```python
	if hand_is_up and time.time() - last_emit[hand] > 0.3:
		 socketio.emit("hand_raised_event", {"hand": hand})
		 last_emit[hand] = time.time()
	```
	En el cliente, añade un guardado similar en `static/js/game.js` para ignorar eventos más rápidos que 200‑300 ms.

6. **Verifica la sincronía**
	- Abre las devtools del navegador y observa los timestamps del canal Socket.IO.
	- Ajusta los umbrales de MediaPipe (`min_detection_confidence`, `min_tracking_confidence`) hasta obtener detecciones estables sin jitter.
	- Si el host tiene GPU, instala `mediapipe` con aceleración (`pip install mediapipe-silicon` no aplica en Linux; mantener la versión oficial) y ejecuta `uv run python api/app.py --reload` para repetir pruebas rápidamente.

Con estas configuraciones el pipeline captura → procesa → emite → ejecuta con menos bloqueos y cada salto del juego responde casi en tiempo real.