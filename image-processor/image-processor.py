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

# Predict using Tensorflow
from tensorflowyolo import TensorflowYolo


my_tf = None
ce_action_type = None
ce_action_source = None
kn_broker_url = None

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
    app.logger.debug(request.headers)

    # app.logger.debug(request.data.decode("utf-8"))
    # data = json.loads(request.data.decode("utf-8"))

    # create a CloudEvent
    event = from_http(request.headers, request.get_data())

    # you can access cloudevent fields as seen below
    app.logger.info(
        f"Found {event['id']} from {event['source']} with type "
        f"{event['type']} and specversion {event['specversion']}"
    )
    app.logger.info(event)

    
    data = event.data

    if 'image' in data and 'time' in data:

        frame = convert_b64jpeg_to_image(data['image'].split(',')[1])

        app.logger.info(data['time'] + " " + str(frame.shape))


        # check / set cam ID
        cam_id = 0
        if 'id' in data:
            cam_id = data['id']


        # Call TF Yolo for object (damage) detection

        start = time.time()
        detected_classes, image_pred = my_tf.predict(frame)
        end = time.time()
        app.logger.info('Predict: Total object detection took {:.5f} seconds'.format(end - start))

        if detected_classes:

            app.logger.info(detected_classes)
            status = 1

            # Create a CloudEvent
            # - The CloudEvent "id" is generated if omitted. "specversion" defaults to "1.0".
            try:
                attributes = {
                    'type': ce_action_type,
                    'source': ce_action_source,
                }
                event_data = {
                    'uuid': str(uuid.uuid4()),  # TO-DO: Please with event uuid
                    'failure': detected_classes,
                    'status': status,
                    'time': data['time']
                }
                event = CloudEvent(attributes, event_data)

                # Creates the HTTP request representation of the CloudEvent in structured content mode
                headers, body = to_structured(event)

                # POST
                requests.post(kn_broker_url, data=body, headers=headers)

            except:
                app.logger.error(f'Failed to send CloudEvent to: {kn_broker_url}')

        else:
            status = 0

        text = data['time']

        # Respond with another event (optional)
        response = make_response({
            'text': text,
            'id': cam_id,
            'status': status,
            'image': convert_image_to_jpeg(image_pred),
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
    app.logger.info("Configure TF based Yolo neural network ...")
    tfmodel_path = os.getenv("TF_MODEL_PATH", default="./tf-model")

    ce_action_type = os.getenv("CE_ACTION_TYPE", default="manuela.image-processor.action")
    ce_action_source = os.getenv("CE_ACTION_SOURCE", default="manuela/eventing/image-processor")
    kn_broker_url = os.getenv("KN_BROKER_URL", default="http://broker-ingress.knative-eventing.svc.cluster.local/sbergste-knative/default")

    my_tf = TensorflowYolo(tfmodel_path=tfmodel_path)

    app.run(debug=False, host='0.0.0.0', port=8080)