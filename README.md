![MANUela Logo](https://github.com/sa-mw-dach/manuela/raw/master/docs/images/logo.png)
# [Manuela](https://github.com/sa-mw-dach/manuela) Showcase: Visual Inspection on OpenShift

This project is a sibling of the MANUela IoT Edge demo project. It shows an exemplary solution blueprint for computer vision visual inspection in manufacturing. 

The demonstrator contains three major parts:
1. Image labeling with the Computer Vision Annotation Tool.
2. Training of a YOLOv4 model for detecting anomalies.
3. Runtime simulation with TensorFlow based serverless inferencing.


Demo Use cases:
- [Annotate images with CVAT running on OpenShift Virtualization](docs/cvat-cnv.md)
- [ML model training with GPUs on OpenShift](ml/README.md)
- [Computer vision object detection on OpenShift Serverless (knative) for messaging and ML model inferencing](docs/runtime.md)

![visual-inspection](images/manu-vi.gif)


*ATTRIBUTION: Paul Bergmann, Michael Fauser, David Sattlegger, Carsten Steger. [MVTec AD](https://www.mvtec.com/company/research/datasets/mvtec-ad) - A Comprehensive Real-World Dataset for Unsupervised Anomaly Detection; in: IEEE Conference on Computer Vision and Pattern Recognition (CVPR), June 2019*