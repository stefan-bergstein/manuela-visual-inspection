import tensorflow as tf
import cv2
import numpy as np
import time


physical_devices = tf.config.experimental.list_physical_devices('GPU')
if len(physical_devices) > 0:
    tf.config.experimental.set_memory_growth(physical_devices[0], True)

from absl import  logging


import core.utils as utils
from core.config import cfg
from core.yolov4 import filter_boxes
from tensorflow.python.saved_model import tag_constants
from PIL import Image


from tensorflow.compat.v1 import ConfigProto
from tensorflow.compat.v1 import InteractiveSession



class Sample:
  name = ''
  average = 0.0
  values = None # list cannot be initialized here!



class Flags:
  tiny = False     # 'yolo or yolo-tiny'
  model = 'yolov4' # 'yolov3 or yolov4'
  iou = 0.45       # 'iou threshold'
  score = 0.25     # 'score threshold'




class TensorflowYolo():



    def __init__(self, tfmodel_path="tf-model", 
                    random_colors=False,
                    framework = 'tf',  # '(tf, tflite, trt')
                    size = 416,
                    probability_minimum=0.5, 
                    threshold = 0.5):

        self.weights = tfmodel_path
        self.random_colors = random_colors
        self.probability_minimum = probability_minimum
        self.threshold = threshold
        self.size = size
        self.framework = framework

        self.FLAGS = Flags()


        config = ConfigProto()
        config.gpu_options.allow_growth = True
        session = InteractiveSession(config=config)
        STRIDES, ANCHORS, NUM_CLASS, XYSCALE = utils.load_config(self.FLAGS)
 

        # load model
        if self.framework == 'tflite':
                self.interpreter = tf.lite.Interpreter(model_path=self.weights)
        else:
                self.saved_model_loaded = tf.saved_model.load(self.weights, tags=[tag_constants.SERVING])


        # Generate colors for representing every detected object
        # with function randint(low, high=None, size=None, dtype='l')


        class_names = utils.read_class_names(cfg.YOLO.CLASSES)
        print(class_names)

        if random_colors:
            self.colors = np.random.randint(0, 255, size=(len(class_names), 3), dtype='uint8')
        else:
            self.colors = array = np.array([[0,255,0] for _ in range(len(class_names))])





    def predict(self, in_image):

        detected_classes = []

        original_image = cv2.cvtColor(in_image, cv2.COLOR_BGR2RGB)

        image_data = cv2.resize(original_image, (self.size, self.size))
        image_data = image_data / 255.

        images_data = []
        for i in range(1):
            images_data.append(image_data)
        images_data = np.asarray(images_data).astype(np.float32)


        start = time.time()

        if self.framework == 'tflite':
            self.interpreter.allocate_tensors()
            input_details = interpreter.get_input_details()
            output_details = interpreter.get_output_details()
            print(input_details)
            print(output_details)
            self.interpreter.set_tensor(input_details[0]['index'], images_data)
            self.interpreter.invoke()
            pred = [self.interpreter.get_tensor(output_details[i]['index']) for i in range(len(output_details))]
            if self.FLAGS.model == 'yolov3' and self.FLAGS.tiny == True:
                boxes, pred_conf = filter_boxes(pred[1], pred[0], score_threshold=0.25, input_shape=tf.constant([self.size, self.size]))
            else:
                boxes, pred_conf = filter_boxes(pred[0], pred[1], score_threshold=0.25, input_shape=tf.constant([self.size, self.size]))
        else:

            infer = self.saved_model_loaded.signatures['serving_default']
            batch_data = tf.constant(images_data)
            pred_bbox = infer(batch_data)

            for key, value in pred_bbox.items():
                boxes = value[:, :, 0:4]
                pred_conf = value[:, :, 4:]

        end = time.time()
        
        print('tf.infer: Object detection took {:.5f} seconds'.format(end - start))
        
        boxes, scores, classes, valid_detections = tf.image.combined_non_max_suppression(
            boxes=tf.reshape(boxes, (tf.shape(boxes)[0], -1, 1, 4)),
            scores=tf.reshape(
                pred_conf, (tf.shape(pred_conf)[0], -1, tf.shape(pred_conf)[-1])),
            max_output_size_per_class=50,
            max_total_size=50,
            iou_threshold=self.FLAGS.iou,
            score_threshold=self.FLAGS.score
        )

        pred_bbox = [boxes.numpy(), scores.numpy(), classes.numpy(), valid_detections.numpy()]

    
        # read in all class names from config
        class_names = utils.read_class_names(cfg.YOLO.CLASSES)

        # by default allow all classes in .names file
        allowed_classes = list(class_names.values())
        
        # custom allowed classes (uncomment line below to allow detections for only people)
        #allowed_classes = ['person']

        detected_classes, image = utils.draw_bbox(original_image, pred_bbox, allowed_classes = allowed_classes)

        image = Image.fromarray(image.astype(np.uint8))
        image = cv2.cvtColor(np.array(image), cv2.COLOR_BGR2RGB)


        return detected_classes, image



