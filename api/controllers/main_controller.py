# main_controller.py
from flask import render_template, Response, send_from_directory

def index():
    # Renderiza la plantilla 'index.html'
    return render_template('index.html')
