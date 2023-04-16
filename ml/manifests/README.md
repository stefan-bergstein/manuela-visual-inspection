

If the `manuela-visual-inspection` project already exixits and was not created with RH-ODS as Data Science Project, please all the labels manually:

```
oc label namespace manuela-visual-inspection "opendatahub.io/dashboard=true" "modelmesh-enabled=true" --overwrite
```

The data connection in `manuela-vi-data-connections.yaml` is for an interal, local S3 server (Noobaa based). Therefore is is *oaky* so save the secrects on GitHub.


