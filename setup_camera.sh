#!/bin/bash

# Detectar el sistema operativo
OS="`uname`"
PYTHON_CMD="python"

# Verificar si Python está instalado
check_python() {
  if command -v python3 &>/dev/null; then
    echo "Python 3 ya está instalado."
  else
    echo "Python 3 no está instalado."
    install_python
  fi
}

# Instalar Python en función del sistema operativo
install_python() {
  if [[ "$OS" == "Linux" ]]; then
    echo "Instalando Python en Linux..."
    sudo apt update
    sudo apt install -y python3 python3-pip
  elif [[ "$OS" == "Darwin" ]]; then
    echo "Instalando Python en macOS..."
    if command -v brew &>/dev/null; then
      brew install python
    else
      echo "Homebrew no está instalado. Instalándolo ahora..."
      /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
      brew install python
    fi
  elif [[ "$OS" == *"_NT"* ]]; then
    echo "Instalando Python en Windows..."
    PYTHON_CMD="python" # En Windows suele ser python
    choco install python3
  else
    echo "Sistema operativo no soportado para la instalación automática de Python."
    exit 1
  fi
}

# Ejecutar Flask y poner la cámara en línea
run_flask() {
  echo "Instalando dependencias de Flask..."
  $PYTHON_CMD -m pip install flask opencv-python

  echo "Ejecutando el servidor Flask..."
  $PYTHON_CMD camera_server.py &

  # Esperar unos segundos para que el servidor Flask arranque
  sleep 5
}

# Obtener la IP local
get_local_ip() {
  if [[ "$OS" == "Linux" || "$OS" == "Darwin" ]]; then
    LOCAL_IP=$(ifconfig | grep inet | awk '$1=="inet" && $2!="127.0.0.1" {print $2}' | grep "192.168.1." | head -n 1)
  elif [[ "$OS" == *"_NT"* ]]; then
    LOCAL_IP=$(powershell.exe -Command "(Get-NetIPAddress -AddressFamily IPv4 | Where-Object {\$_.IPAddress -like '192.168.1.*'}).IPAddress" | tr -d '\r')
  fi
  echo "La IP local es: $LOCAL_IP"
}

# Crear una variable de entorno con la IP local
set_env_variable() {
  export STREAM_URL="http://$LOCAL_IP:5001/video_feed"
  echo "La variable STREAM_URL se ha configurado como: $STREAM_URL"
}

# Reemplazar la IP en el archivo Python donde se usa el stream_url
replace_ip_in_python() {
  # Asegúrate de que STREAM_URL esté en una sola línea
  STREAM_URL=$(echo "$STREAM_URL" | tr -d '\n')

  # Reemplazar en game_controller.py
  sed -i.bak "s|stream_url = .*|stream_url = '$STREAM_URL'|g" api/controllers/game_controller.py
  echo "stream_url se ha actualizado en game_controller.py."

  # Reemplazar en video_controller.py
  sed -i.bak "s|stream_url = .*|stream_url = '$STREAM_URL'|g" api/controllers/video_controller.py
  echo "stream_url se ha actualizado en video_controller.py."
}

# Verificar si la imagen de Docker existe, si no, crearla
check_docker_image() {
  IMAGE_NAME="cianbatllo-app"  # Cambia este nombre por el que uses

  if [[ "$(docker images -q $IMAGE_NAME 2> /dev/null)" == "" ]]; then
    echo "La imagen de Docker no existe. Creándola ahora..."
    docker-compose build
  else
    echo "La imagen de Docker ya existe."
  fi
}

run_docker() {
  echo "Verificando la imagen de Docker..."
  check_docker_image

  echo "Ejecutando el servidor Docker..."
  docker-compose up -d

  # Esperar unos segundos para que el servidor Flask arranque
  sleep 5
}

# Ejecutar los pasos
check_python
run_flask
get_local_ip
set_env_variable
replace_ip_in_python
run_docker

echo "Configuración completa."
