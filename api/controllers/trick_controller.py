# game_controller.py
from flask import render_template,Response
import cv2
import mediapipe as mp


def trick():
    # Renderiza la plantilla 'index.html'
    return render_template('trick.html')
