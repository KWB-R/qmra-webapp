#! bin/bash
set -e

# add admin user
adduser k8admin
usermod -aG sudo k8admin
su - k8admin

sudo apt update && sudo apt upgrade -y

# install microk8s
sudo snap install microk8s --classic --channel=1.31
# add the user
sudo usermod -a -G microk8s $(echo $USER)
mkdir -p ~/.kube
chmod 0700 ~/.kube
newgrp microk8s
# copy the kube config (for k9s)
cd .kube
microk8s config > config
# microk8s status --wait-ready

# install kubectl
sudo snap install kubectl --classic
kubectl config use-context microk8s

# install k9s
wget https://github.com/derailed/k9s/releases/download/v0.32.5/k9s_linux_amd64.deb && sudo apt install ./k9s_linux_amd64.deb && rm k9s_linux_amd64.deb

# put the aliases in bash_aliases
cat <<EOF > .bash_aliases
alias mk8='microk8s'
alias k8='microk8s kubectl'
alias helm='microk8s helm'
alias sudo='sudo '
EOF
source .bash_aliases

# enable add-ons
mk8 enable ingress cert-manager hostpath-storage metrics-server
mk8 disable ha-cluster
#observability dashboard hostpath-storage

# firewall settings:
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow https
#ufw allow http #necessary for certbot to obtain certificate
sudo ufw enable
# needed by mk8s hostpath-provisionner:
sudo ufw default allow routed