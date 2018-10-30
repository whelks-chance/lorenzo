# lorenzo

### CKAN importing of bids_ data

See other repositories for the install guide...

https://github.com/ckan/ckan/issues/2769#issuecomment-173625344


## CKAN
source /home/ianh/ckan/lib/default/bin/activate
paster serve /etc/ckan/default/development.ini


## DataPusher
source /home/ianh/datapusher/datapusher_env/bin/activate
cd datapusher/
python datapusher/main.py deployment/datapusher_settings.py


## ckanext-ckanpackager
https://github.com/whelks-chance/ckanext-ckanpackager

source /home/ianh/ckan/lib/default/bin/activate
paster setup.py develop


## CKAN packager - celery pool
https://github.com/whelks-chance/ckanpackager

source /home/ianh/ckanpackager_service_venv/bin/activate
cd /home/ianh/PycharmProjects/ckanpackager_service/ckanpackager
CKANPACKAGER_CONFIG=/home/ianh/PycharmProjects/ckanpackager_service/ckanpackager/ckanpackager/config_defaults.py python ckanpackager/service.py


## CKAN packager - celery worker - fast
source /home/ianh/ckanpackager_service_venv/bin/activate
CKANPACKAGER_CONFIG=/home/ianh/PycharmProjects/ckanpackager_service/ckanpackager/ckanpackager/config_defaults.py celery -A ckanpackager.task_setup.app --events --concurrency=1 --maxtasksperchild=1000 --queues=fast --hostname=fast.%h worker --loglevel=INFO

### extra configs
--detach


## CKAN packager - celery worker - slow