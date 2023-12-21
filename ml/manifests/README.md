# CLI based setup of RHDOS for Manu-vi model serving

**Warning - this part is experimental**

## Provide local S3 Storage
Model Serving requires a S3 bucket with an ACCESS_KEY and SECRET_KEY. In case you don't have S3 already available (e.g. ODF or on AWS) you can deploy Minio on your OpenShift Cluster:

```         
oc apply -f https://raw.githubusercontent.com/mamurak/os-mlops/master/manifests/minio/minio.yaml
```

- Minio is deployed to the project/namespace `minio`.
- Launch the minio web UI (see Route) and create a bucket (e.g. `manu-vi`).

## Load a pre-train model into minio bucket (the lazy way)

```
**The following approach does not work anymore with the latest version of minio. Please use S3 CLI/API**

BUCKET=manu-vi

oc exec -n minio deploy/minio -- mkdir -p data/${BUCKET}

oc exec -n minio deploy/minio -- curl -L https://github.com/stefan-bergstein/manuela-visual-inspection/releases/download/v0.3-alpha-pytorch-rhods/manu-vi-best-yolov5m.onnx -o data/${BUCKET}/manu-vi-best.onnx
```

## Create Data Science Project from exiting OpenShift project

If the `manuela-visual-inspection` project already exists and was not created with RH-ODS as Data Science Project, please all the labels manually:

```
oc label namespace manuela-visual-inspection "opendatahub.io/dashboard=true" "modelmesh-enabled=true" --overwrite
```

## Create Data Connection

The data connection in `manuela-vi-data-connections.yaml` is for an internal, local S3 server (minio based). Therefore is is *oaky* so save the secrect on GitHub.

  - Name: `manu-vi`
  - AWS_ACCESS_KEY_ID: `minio`
  - AWS_SECRET_ACCESS_KEY: `minio123`
  - AWS_S3_ENDPOINT: `http://minio-service.minio.svc.cluster.local:9000`
  - AWS_S3_BUCKET: `manu-vi`

```
oc apply -f manuela-vi-data-connections.yaml
```

## Create model server (ServingRuntime)

```
oc apply -f manuela-vi-servingruntime.yaml
```

Check runtime:
```
oc get ServingRuntime -A
```
Example output
```
NAMESPACE                   NAME                              DISABLED   MODELTYPE     CONTAINERS   AGE
manuela-visual-inspection   manu-vi                                      openvino_ir   ovms         5m14s
```

## Create InferenceService 

```
oc apply -f manuela-vi-inference-service.yaml
```

Check runtime:
```
oc get InferenceService -A
```

Example output:
```
NAMESPACE                   NAME        URL                                                       READY   PREV   LATEST   PREVROLLEDOUTREVISION   LATESTREADYREVISION   AGE
manuela-visual-inspection   manu-vi     grpc://modelmesh-serving.manuela-visual-inspection:8033   True                                                                  3m24s
```
