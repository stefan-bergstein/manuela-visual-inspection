# Build container images

## Setup secret for Quay.io credentials

### Option 1: Use your personal Quay.io account
to-do: describe steps

### Option 2: Use Red Hat's Manuela Quay.io account
- Login to Quay.io
- Navigate to manuela repo
- Navigate tomanuela+build robot account
- View credentials
- Download manuela-build-secret.yml to secrets/


- Push and link secret:
```
oc apply -f secrets/manuela-build-secret.yml -n manuela-visual-inspection
oc secret link pipeline manuela-build-pull-secret -n manuela-visual-inspection
```


## Deploy Pipeline and start runs
```
oc apply -k .
``````