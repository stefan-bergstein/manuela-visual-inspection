# Extend share memory for your notebook 
See also [YOLOv5 Transfer Learning on RHODS](https://github.com/rh-aiservices-bu/yolov5-transfer-learning#environment-and-prerequisites)


PyTorch is internally using shared memory (`/dev/shm`) to exchange data between its internal worker processes. However, default container engine configurations limit this memory to the bare minimum, which can make the process exhaust this memory and crash. The solution is to manually increase this memory by mounting a emptyDir volume or to run the model training without PyTorch workers (which will slowdown the training).

## Shut down your workbench.
First, shut down your workbench in the RH-ODS Data Science Project before patching the Notebook manifest.


## Find your notebook

List all Notebooks in your Data Science Project:
```
oc get Notebook -n manuela-visual-inspection
```

Example output:
```
NAME      AGE
manu-vi   6m4s
```

## Extend the default shared memory

Patch the notebook with a `emptyDir` volume for `/dev/shm`. 

If needed, replace the notebook and namespace name with your values.

```
oc patch Notebook manu-vi -n manuela-visual-inspection  --type=json --patch '
[
  { 
    "op": "add",
    "path": "/spec/template/spec/containers/0/volumeMounts/-",
    "value": 
        {
            "name": "dshm",
            "mountPath": "/dev/shm"
        }
  },
  { 
    "op": "add",
    "path": "/spec/template/spec/volumes/-",
    "value": {
            "name": "dshm",
            "emptyDir": {
                "medium": "Memory"
            }
        }
  }
]'
```

In case of trouble, try the manual procedure described in  [YOLOv5 Transfer Learning on RHODS](https://github.com/rh-aiservices-bu/yolov5-transfer-learning#environment-and-prerequisites).
