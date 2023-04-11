import sys
import time
import cv2
import os
import argparse
import json
import datetime
import numpy as np

from PIL import Image

from kafka import KafkaProducer
from random import shuffle
import base64

from cloudevents.http import CloudEvent, to_structured
import requests
import uuid

import logging

#
# Globals
#
web_server=None

# Logging
module = sys.modules['__main__'].__file__
logger = logging.getLogger(module)

# Kafka
send_kafka = False
producer = None
topic = None
cam_id = 0
fps = 1

#
# Sending message via REST Web Services Cloud Event
#

def send_cloud_event(msg):

    ce_action_type = "manuela.cam-sim.image"
    ce_action_source = "manuela/eventing/cam-sim"

    # Create a CloudEvent
    # - The CloudEvent "id" is generated if omitted. "specversion" defaults to "1.0".
    try:
        attributes = {
            'type': ce_action_type,
            'source': ce_action_source,
        }

        event = CloudEvent(attributes, msg)

        # Creates the HTTP request representation of the CloudEvent in structured content mode
        headers, body = to_structured(event)

        # POST
        requests.post(web_server, data=body, headers=headers)

    except:
        logger.error(f'Failed to send CloudEvent to: {web_server}')

    return


#
# Send message via REST Web Services or kafka
#

def send_msg(msg):
    if send_kafka:
        producer.send(topic, msg)
    else:
        # Send msg via REST
        send_cloud_event(msg)
    return

#
# Convert image frame to base64 jpeg
#

def convert_image_to_jpeg(image):
    # Encode frame as jpeg
    frame = cv2.imencode('.jpg', image)[1].tobytes()
    # Encode frame in base64 representation and remove utf-8 encoding
    frame = base64.b64encode(frame).decode('utf-8')
    return "data:image/jpeg;base64,{}".format(frame)


def scale_frame(frame, scale):
    # Scale frame
    frameHeight, frameWidth = frame.shape[:2]
    frameWidth = int(frameWidth * scale)
    frameHeight = int(frameHeight * scale)
    return cv2.resize(frame, (frameWidth, frameHeight))


#
# Read image files from disk
#

def find_images(path):
    # Find images on disk

    image_list = []
    
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith("png") or file.endswith("jpg"):
                image_meta =  {"label": "good", "path": "data/0.png" }
                ipath = os.path.join(root, file)
                label = os.path.basename(root).replace(" ", "-").lower()
                image_meta["label"] = label
                image_meta["path"] = ipath
                image_list.append(image_meta)
    return image_list


def read_imagefiles(path, fps, scale):
    logger.info("Read image files from disk ...")

    wait_time = (1/fps)

    # Get image list ans shuffle
    image_list = find_images(path)
    shuffle(image_list)

    i=0
    while True:
        # Empty Message 
        msg = {     
            "image": "empty",   
            "id": cam_id,
            "type": "image",
            "time": "empty",
            "text": "empty",
            "label": "empty"                
        }   

        # Read image from disk
        logger.info(f"Imagae {i}: {image_list[i]}" )

        image_meta = image_list[i]           
        pil_image = Image.open(image_meta["path"]) 
        frame = np.array(pil_image, "uint8")
        msg['label'] = image_meta["label"]
        
        i = i + 1
        if i == len(image_list):
            i = 0

        # Scale frame
        frame = scale_frame(frame, scale)

        msg['time'] = str(datetime.datetime.now())
        msg['text'] = msg['time']
        msg['image'] = convert_image_to_jpeg(frame)

        send_msg(msg)

        logger.info("Message sent: " +topic + " - " + msg['time'] + " - " + str(frame.shape))

        time.sleep(wait_time)

    return

def connect_kafka(bootstrap_servers, security_protocol, ssl_check_hostname, ssl_cafile):

    logger.info(f"Connect to kafka bootstrap_servers: {bootstrap_servers} " )
    logger.info(f"- security_protocol: {security_protocol}")
    logger.info(f"- ssl_check_hostname: {ssl_check_hostname}")
    logger.info(f"- ssl_cafile: {ssl_cafile}")

    producer = KafkaProducer(bootstrap_servers=bootstrap_servers,
        value_serializer=lambda m: json.dumps(m).encode('utf-8'),
        security_protocol=security_protocol,
        ssl_check_hostname=ssl_check_hostname,
        batch_size=0,
        linger_ms=10,
        max_request_size=5048576,
        ssl_cafile=ssl_cafile)

    return producer


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Cam simulator Client')

    # Rest web server settings

    parser.add_argument(
            '--rest',  action="store_true",
            help='Use REST web client for sending images [default: False]')

    parser.add_argument(
            '--server',  type=str, default='http://localhost:8088',
            help='Image receiver address (REST web server) [default: http://localhost:8088]')


    # Kafka settingsFalse

    parser.add_argument(
            '--topic',  type=str, default='visual-inspection-images',
            help='Kafka topic [default: visual-inspection-images]')

    parser.add_argument(
            '--bootstrap',  type=str, default='localhost:9092',
            help='Kafka bootstrap servers [default: localhost:9092]')

    parser.add_argument( 
            '--ssl',  action="store_true",
            help='Use SSL for Kafka [default: no ssl]')

    parser.add_argument(
            '--check_hostname',  action="store_true",
            help='SSL check hostname for Kafka [default: false]')    

    parser.add_argument(
            '--cafile',  type=str, default='./ca.crt',
            help='SSL CA file for for Kafka [default: ./ca.crt]')



    # Stream images settings 

    parser.add_argument(
            '--images',  action="store_true",
            help='Stream images')

    parser.add_argument(
            '--path',  type=str, default='data',
            help='Path of the image directory')

    parser.add_argument(
            '--fps',  type=float, default=10.0,
            help='Frames per second')    


    parser.add_argument(
            '--scale',  type=float, default=1.0,
            help='Scale images. Default 1.0')


    parser.add_argument(
            '--camid', type=str, default='0',
            help='ID number for the simulated camera')
    
    parser.add_argument('-l', '--log-level', default='WARNING',
                                help='Set log level to ERROR, WARNING, INFO or DEBUG')

    args = parser.parse_args()

   
    #
    # Configure logging
    #

    try:
        logging.basicConfig(stream=sys.stderr, level=args.log_level, format='%(name)s (%(levelname)s): %(message)s')
    except ValueError:
        logger.error("Invalid log level: {}".format(args.log_level))
        sys.exit(1)

    logger.info("Log level set: {}".format(logging.getLevelName(logger.getEffectiveLevel())))

    #
    # Kafka setting via env vars
    #

    topic = os.getenv("TOPIC", default=args.topic)
    bootstrap_servers = os.getenv("BOOTSTRAP_SERVER", default=args.bootstrap)
    security_protocol = os.getenv("SECURITY_PROTOCOL", default="PLAINTEXT")
    ssl_check_hostname = bool(os.getenv("SSL_CHECK_HOSTNAME", default="FALSE").lower() == 'true') or args.check_hostname

    ssl_cafile = os.getenv("SSL_CAFILE", default=args.cafile)

    # ID number for the simulated camera
    cam_id = int(os.getenv("CAMID", default=args.camid))


    fps = float(os.getenv("FPS", default=args.fps))

    #
    # Connect to target either to web socket or kafka
    #

    web_server = args.server

    if args.rest:
        send_kafka = False
    else:
        send_kafka = True

    if send_kafka:

        topic = args.topic
        
        if security_protocol == "PLAINTEXT":
            if args.ssl:
                security_protocol="SSL"
            else:
                security_protocol="PLAINTEXT"

        # To-Do: Add exception handling and retries
        producer = connect_kafka(bootstrap_servers, security_protocol, ssl_check_hostname, ssl_cafile)

    #
    # Start the work ...
    #
     
    read_imagefiles(args.path, fps, args.scale)

