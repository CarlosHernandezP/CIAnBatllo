# game_controller.py
from flask import render_template

def game():
    # Renderiza la plantilla 'index.html'
    return render_template('game.html')