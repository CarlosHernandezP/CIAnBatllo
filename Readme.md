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


## Execute:
To execute the api, type flask run inside api folder

## Docker Setup:

### Prerequisites:
- Docker
- Docker Compose

### Steps to run the application using Docker:

1. Make sure you have Docker and Docker Compose installed on your system.

2. Clone the repository and navigate to the project directory.

3. Build and run the Docker containers:
   ```
   docker-compose up --build
   ```

4. The application will be available at `http://localhost:5000`.

### Additional Information:

- The Dockerfile uses Python 3.8.10 as the base image and installs all necessary dependencies.
- The docker-compose.yml file sets up the service and maps port 5000 of the container to port 5000 on your host machine.
- The application's code is mounted as a volume, allowing for real-time code changes without rebuilding the container.

### Troubleshooting:

If you encounter any issues with the camera access, make sure to run the `setup_camera.sh` script:
