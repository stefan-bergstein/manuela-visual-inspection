# Model training for the Metal Nut Data Set
Automating Visual Inspections with AI on [Red Hat OpenShift Data Science](https://www.redhat.com/en/technologies/cloud-computing/openshift/openshift-data-science) - Hands-on tutorial

## Prerequisites

### OpenShift with GPU worker nodes 
GPU worker node are not mandatory, but recommended when you would like to train the model by yourself.

- Redhatters can order the ["NVIDIA GPU Operator Red Hat OpenShift Container Platform 4 Workshop"](https://demo.redhat.com/catalog?search=Nvidia). Please be aware of the costs and shutdown the service.

- Upgrade OpenShift to 4.11.x

- Install the [Node Feature Discovery (NFD) Operator](https://docs.nvidia.com/datacenter/cloud-native/gpu-operator/openshift/install-nfd.html#installing-the-node-feature-discovery-nfd-operator).

- Install the [NVIDIA GPU Operator](https://docs.nvidia.com/datacenter/cloud-native/gpu-operator/openshift/install-gpu-ocp.html#installing-the-nvidia-gpu-operator).

- Create the [ClusterPolicy instance](https://docs.nvidia.com/datacenter/cloud-native/gpu-operator/openshift/install-gpu-ocp.html#create-the-clusterpolicy-instance).

- Verify the [successful installation of the NVIDIA GPU Operator](
https://docs.nvidia.com/datacenter/cloud-native/gpu-operator/openshift/install-gpu-ocp.html#verify-the-successful-installation-of-the-nvidia-gpu-operator).

### Deploy the RHODS Operator
Follow ["Installing OpenShift Data Science on OpenShift Container Platform"]
(https://access.redhat.com/documentation/en-us/red_hat_openshift_data_science_self-managed/1.22/html-single/installing_openshift_data_science_self-managed/index#installing-openshift-data-science-on-openshift-container-platform_install)


### Provide S3 Storage
Model Serving requires a S3 bucket with an ACCESS_KEY and SECRET_KEY. In case you don't have S3 already available (e.g. ODF or on AWS) you can deploy Minio on your OpenShift Cluster:

```         
oc apply -f https://raw.githubusercontent.com/mamurak/os-mlops/master/manifests/minio/minio.yaml
```

- Minio is deployed to the project/namespace `minio`.
- Launch the minio web UI (see Route) and create a bucket (e.g. `manu-vi`).

## Model training

### Create new RHODS workbench for Ultralytics Pytorch Yolov5

- Launch RHODS via the application launcher (nine-dots) -> **`Red Hat OpenShift Data Science`**
- [Create a new Data Science project](../images/create-data-science-workbench-gpu-cuda.png) -> **`Create data science project`**.

  If you have your own OpenShift cluster, you can name the project 'manuela-visual-inspection'. If not add your initials. E.g. 'manu-vi-stb'.
  Don't choose to long names, because project and model server names are internally concatenated, which could lead into problems.

  - Name: `manu-vi`
  - Resource name: `manu-vi`
  - -> **`Create`**.

- Create a data connection with your S3 configuration
  - Data connections -> **`Add Data connections`**.
  - Name: `manu-vi`
  - AWS_ACCESS_KEY_ID: `minio`
  - AWS_SECRET_ACCESS_KEY: `minio123`
  - AWS_S3_ENDPOINT: `http://minio-service.minio.svc.cluster.local:9000`
  - AWS_S3_BUCKET: `manu-vi`

- Create new RHODS workbench
  - Workbenches -> **`Create workbench`**.
  - Name: `manu-vi`
  - Image: `CUDA` (assuming you have a cluster with a Nvidia GPU)
  - Deployment size: `Medium` 
  - Cluster storage: `Create new cluster storage`
  - Data connection: `Use existing data connection` -> `manu-vi`
  - -> **`Create workbench`**.

- Extend share memory for your notebook

  PyTorch is internally using shared memory (/dev/shm) to exchange data between its internal worker processes. However, default container engine configurations limit this memory to the bare minimum, which can make the process exhaust this memory and crash. The solution is to manually increase this memory by mounting a emptyDir volume or to run the model training without PyTorch workers (which will slowdown the training).

  - Patch the Notebook as described here: [README.md](https://github.com/stefan-bergstein/manuela-visual-inspection/blob/main/ml/pytorch/README)
  - Stop and start your workbench in your Data Science Project

- Open the workbench and clone https://github.com/stefan-bergstein/manuela-visual-inspection.git

### Explore and run the model training notebook
- Navigate to `manuela-visual-inspection/ml/pytorch` and open  `Manuela_Visual_Inspection_Yolov5_Model_Training.ipynb`
- Explore or explain and run cells step by step
  - Setup and test the Ultralytics Yolov5 toolkit
  - Inspect training dataset (image and labels)  
  - Model training and validation
  - Convert model to onnx format and upload it to S3

## Model Serving

### Optionally, download a pre-trained manu-vi model and upload it to S3
In you have to not had the time or resources to train the model by yourself, you can download a pre-trained manu-vi model and upload it to your S3 bucket.
- Open your workbench (with your manu-vi data connection)
- Navigate to `manuela-visual-inspection/ml/pytorch` and open `Upload_pretrained_model.ipynb`
- Run the notebook to upload the model

### Configure RHODS model serving
- Create model server in your data science project
  - Models and model servers ->  **`Configure server`**
  - Number of model server replicas to deploy: `1`
  - Model server size: `Small`
  - Model route: -> `Check/Enable` *'Make deployed models available through an external route'*
  - Token authorization ->  `Uncheck/Disable` *'Require token authentication'*
  - -> **`Configure`**

- Deploy the trained model -> **`Deploy Model`**
  - Model Name: `manu-vi`
  - Model framework: `onnx - 1`
  - Model location: `Existing data connection`
  - Name: `manu-vi`
  - Folder path:  `manu-vi-best.onnx`
  - -> **`Deploy`**

- Wait until Status is green / loaded
  - Copy and save the inference URL

## Test interfering with a REST API call
Show how an ML REST call could be integrated into your 'intelligent' Python application.

- Return to the workbench
- Navigate to `manuela-visual-inspection/ml/pytorch` and open  `Manuela_Visual_Inspection_Yolov5_Infer_Rest.ipynb` 
- Study or explain and run cells step by step
  - Please don´t forget to update the inferencing URL 
- Demonstrate cool inferencing with RHODS :-)   

