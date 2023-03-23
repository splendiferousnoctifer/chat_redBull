set -e

echo " -- update certificates"
sudo "./Install Certificates.command"


echo " -- creating virtual environment"

pip3 install -r requirements.txt

make start
