import logging
from flask import Flask, request, make_response, render_template
from flask_socketio import SocketIO
import json


app = Flask(__name__)
sio = SocketIO(app, logger=True, engineio_logger=False)

#
# HTML Pages
#

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/cam')
def cam():
    return render_template('cam.html')

@app.route('/avi')
def avi():
    return render_template('avi.html')


#
# From Cam/Screen to UI connections
#

@sio.on('connect', namespace='/ui')
def connect_ui():
    print('ui client connected: {}'.format(request.sid))


@sio.on('disconnect', namespace='/ui')
def disconnect_ui():
    print('ui client disconnected: {}'.format(request.sid))


@sio.on('connect', namespace='/cam')
def connect_cam():
    print('[Cam client connected: {}'.format(request.sid))


@sio.on('disconnect', namespace='/cam')
def disconnect_cam():
    print('Cam client disconnected: {}'.format(request.sid))


@sio.on('cam2server', namespace='/cam')
def handle_cam_message(message):
    # print('Send msg to server2ui')
    sio.emit('server2ui', message, namespace='/ui')


#
# Rest / Cloud Event to AVI page
#

@sio.on('connect', namespace='/ui2')
def connect_ui2():
    print('ui2 client connected: {}'.format(request.sid))

@sio.on('disconnect', namespace='/ui2')
def disconnect_ui2():
    print('ui2 client disconnected: {}'.format(request.sid))



@app.route('/', methods=['POST'])
def process_event():
    app.logger.debug(request.headers)
    app.logger.debug(request.data.decode("utf-8"))
    data = json.loads(request.data.decode("utf-8"))

    sio.emit('server2ui2', data, namespace='/ui2')


    response = make_response({})
    return response

if __name__ == '__main__':

    app.logger.setLevel(logging.DEBUG)
    sio.run(app=app, host='0.0.0.0', port=8080)

