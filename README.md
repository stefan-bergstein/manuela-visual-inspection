![MANUela Logo](https://github.com/sa-mw-dach/manuela/raw/master/docs/images/logo.png)
# [Manuela](https://github.com/sa-mw-dach/manuela) Showcase: Visual Inspection on OpenShift

This project is a sibling of the MANUela IoT Edge demo project. It shows an exemplary solution blueprint for computer vision visual inspection in manufacturing. 

The demonstrator contains 2x3 parts. The ML infrastructure sections covers use cases of MLOps and DevOps engineers.
Data and ML engineers would focus on the ML application tasks.


## ML Infrastructure
1. [Deploy and manage the Computer Vision Annotation Tool (CVAT) on OpenShift Virtualization.](docs/cvat-cnv.md#install-cvat-in-a-openshift-virtualization-virtual-machine)
1. [Jupyter notebook as a Service with OpenShift Data Science. ](ml/README.md)
1. [Serverless (knative) images processing on OpenShift.](docs/runtime.md#installation)

## ML Application
1. [Image labeling with the Computer Vision Annotation Tool.](docs/cvat-cnv.md#image-labeling-with-the-computer-vision-annotation-tool)
1. [Training of a computer vision AI model for detecting anomalies in images with PyTorch YOLOv5).](ml/README.md)
1. [Real-time manufacturing defect detection with Model Mesh based inferencing.](docs/runtime.md#demo-execution)





![visual-inspection](images/manu-vi.gif)


*ATTRIBUTION: Paul Bergmann, Michael Fauser, David Sattlegger, Carsten Steger. [MVTec AD](https://www.mvtec.com/company/research/datasets/mvtec-ad) - A Comprehensive Real-World Dataset for Unsupervised Anomaly Detection; in: IEEE Conference on Computer Vision and Pattern Recognition (CVPR), June 2019*