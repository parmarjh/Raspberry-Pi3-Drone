#!/usr/bin/env python
from importlib import import_module
import socket
import io
import os
from multiprocessing import Process
import sys
from flask import Flask, render_template, Response, request

import ardrone

from base_camera import BaseCamera  # Hard code using web cam

# Raspberry Pi camera module (requires picamera package)
# from camera_pi import Camera

app = Flask(__name__)

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

@app.route('/pic/<string:address>', methods= ["GET"])
def pic(address):
    return app.send_static_file(address)

# background process happening without any refreshing
@app.route('/background_process_test', methods=['POST'])
def background_process_test():
    if request.method == 'POST':
      direction_action = request.form.get('direction')
      if direction_action == 'left':
        drone.move_left()
      elif direction_action == 'right':
        drone.move_right()
      elif direction_action == 'forward':
        drone.move_forward()
      elif direction_action == 'backward':
        drone.move_backward()
      elif direction_action == 'land':
        drone.land()
      elif direction_action == 'takeoff':
        drone.takeoff()
      elif direction_action == 'rotleft':
        drone.turn_left()
      elif direction_action == 'rotright':
        drone.turn_right()
      elif direction_action == 'up':
        drone.move_up()
      elif direction_action == 'hover':
        drone.hover()
      elif direction_action == 'down':
        drone.move_down()
      elif direction_action == 'emergency':
        drone.reset()
      elif direction_action == 'x':
        drone.hover()
      elif direction_action == 'trim':
        drone.trim()
      elif direction_action == 'exit':
        raise RuntimeError("down")
    return "nothing"


@app.route('/', methods=['GET', 'POST'])
def index():
    """Video streaming home page."""
    return render_template('index.html')

@app.route('/navdata', methods=['GET'])
def navdat():
    """Video streaming home page."""
    nvdt = 'Battery: '+drone.navdata['demo']['battery']+' Altitude: '+drone.navdata['demo']['altitude']
    return nvdt

def gen(camera):
    """Video streaming generator function."""
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(BaseCamera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

def dgen():
    """Video streaming generator function."""
    frame = io.BytesIO()
    while True:
        drone.image.save(frame, "JPEG")
        yield (b'--frame1\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/drone_feed')
def drone_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(dgen(),
                    mimetype='multipart/x-mixed-replace; boundary=frame1')

if __name__ == '__main__':
    drone = ardrone.ARDrone()
    my_ip = get_ip()
    sys.stderr.write(app.instance_path)
    try:
       app.run(host=my_ip, threaded=True)
    except RuntimeError, msg:
       if str(msg) == "down":
        drone.land()
        drone.halt()
        exit()          
