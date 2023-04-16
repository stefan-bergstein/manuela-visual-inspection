from cloudevents.conversion import to_structured
from cloudevents.http import CloudEvent, from_http



import requests
import numpy as np
import cv2
import datetime
from PIL import Image
import base64
import pprint

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

def scale_frame(frame, scale):
    # Scale frame
    frameHeight, frameWidth = frame.shape[:2]
    frameWidth = int(frameWidth * scale)
    frameHeight = int(frameHeight * scale)
    return cv2.resize(frame, (frameWidth, frameHeight))


def test_func():
    # Create a CloudEvent
    # - The CloudEvent "id" is generated if omitted. "specversion" defaults to "1.0".
    attributes = {
        "type": "dev.knative.function",
        "source": "https://knative.dev/python.event",
    }



    # Empty Message 
    data = {     
        "image": "empty",   
        "id": 0,
        "type": "image",
        "time": "empty",
        "text": "empty",
        "label": "empty"                
    }  


    # Read image from disk       
    pil_image = Image.open("scratch-012.png") 
    frame = np.array(pil_image, "uint8")
    data['label'] = "scratch-012.png"

    # Scale frame
    scale = 0.5
    frame = scale_frame(frame, scale)

    data['time'] = str(datetime.datetime.now())
    data['text'] = data['time']
    data['image'] = convert_image_to_jpeg(frame)

    event = CloudEvent(attributes, data)

    # Creates the HTTP request representation of the CloudEvent in structured content mode
    headers, body = to_structured(event)

    try:
        response = requests.post("http://127.0.0.1:8080", data=body, headers=headers, verify=False)
    except:
        print("ERROR: Failed to establish connection")
        raise
        # create a CloudEvent

    data = response.json()
    print("Returned cloud event:")
    print(response.json())
    print("response.status_code: ", response.status_code)
    print(response.headers['Ce-Type'])


    if response.status_code == 200 and response.headers['Ce-Type'] == "manuela.image-processor.response":
        frame = convert_b64jpeg_to_image(data['image'].split(',')[1])
        cv2.imwrite("out.jpeg", frame)
        print("prediction image saved: out.jpeg")
    else:
        print("something went wrong :-(")

if __name__ == "__main__":
  test_func()