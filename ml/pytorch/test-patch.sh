# oc patch   Notebook manu-vi -n manuela-visual-inspection  --type=json  --dry-run=client -o yaml --patch '
oc patch   Notebook manu-vi -n manuela-visual-inspection  --type=json --patch '
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

