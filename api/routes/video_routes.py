# main_routes.py
from flask import render_template, Response, request
from controllers.video_controller import  video_feed, video
from flask import Blueprint

video_routes = Blueprint('video_routes', __name__)

@video_routes.route('/video')
def video_route():
    return video()

@video_routes.route('/video_feed')
def video_feed_route():
    return video_feed()
