import os
import time
import logging

from flask import Flask, request, make_response
from cloudevents.http import CloudEvent, to_structured, from_http

import requests

import uuid
import cv2
import json
import base64
import numpy as np

from remote_infer_rest import ort_v5

infer_url = None

def convert_b64jpeg_to_image(b64jpeg):

    # Decode base64 string in bytes
    img_bytes = base64.b64decode(b64jpeg)
  
    # Convert in np array 
    jpg_as_np = np.frombuffer(img_bytes, dtype=np.uint8)

    # Decode into cv2 image
    return cv2.imdecode(jpg_as_np, flags=1) 

def convert_image_to_jpeg(image):
    # Encode frame as jpeg
    frame = cv2.imencode('.jpg', image)[1].tobytes()

    # Encode frame in base64 representation and remove utf-8 encoding
    frame = base64.b64encode(frame).decode('utf-8')
    return "data:image/jpeg;base64,{}".format(frame)

app = Flask(__name__)

@app.route('/', methods=['POST'])
def process_image():
    # app.logger.debug(request.headers)

    # create a CloudEvent
    event = from_http(request.headers, request.get_data())

    # you can access cloudevent fields as seen below
    app.logger.info(
        f"Found {event['id']} from {event['source']} with type "
        f"{event['type']} and specversion {event['specversion']}"
    )
    # app.logger.info(event)

    data = event.data

    if 'image' in data and 'time' in data:

        frame = convert_b64jpeg_to_image(data['image'].split(',')[1])

        app.logger.info(data['time'] + " " + str(frame.shape))


        # check / set cam ID
        cam_id = 0
        if 'id' in data:
            cam_id = data['id']


        # Call Model Mesh for object (damage) detection

        # Define classes file
        classes_file = 'data.yaml'

        #  Set Confidence threshold, between 0 and 1 (detections with less score won't be retained)
        conf = 0.2

        #  Intersection over Union Threshold, between 0 and 1 (cleanup overlapping boxes)
        iou = 0.4

        # Inferencing
        start = time.time()

        infer=ort_v5(frame, infer_url, conf, iou, 640, classes_file)
        img, out, result = infer()

        end = time.time()
        app.logger.info('Predict: Total object detection took {:.5f} seconds'.format(end - start))

        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                           
        # check if something was detected
        if list(out.shape)[0] > 0:
            status = 1
        else:
            status = 0

        text = data['time']

        # Respond with another event 
        response = make_response({
            'text': text,
            'id': cam_id,
            'status': status,
            'image': convert_image_to_jpeg(img),
        })
        response.headers["Ce-Id"] = str(uuid.uuid4())
        response.headers["Ce-specversion"] = "1.0"
        response.headers["Ce-Source"] = "manuela/eventing/image-processor"
        response.headers["Ce-Type"] = "manuela.image-processor.response"
    else:
        app.logger.warning("Payload not valid.")
        response = make_response({
            'msg': 'Payload not valid'
        })
    return response


if __name__ == '__main__':

    app.logger.setLevel(logging.DEBUG)
    app.logger.info("Start image processor ...")

    infer_url = os.getenv("INFER_URL", default="https://manuela-vi-onnx-ods-project-stefan.apps.ocp5.stormshift.coe.muc.redhat.com/v2/models/manuela-vi-onnx/infer")

    app.run(debug=False, host='0.0.0.0', port=8080)