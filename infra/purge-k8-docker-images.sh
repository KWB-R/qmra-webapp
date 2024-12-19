!# /bin/bash

crictl -r unix:///var/snap/microk8s/common/run/containerd.sock rmi --prune