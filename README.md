# flask-https-example

```
source venv/bin/activate
pip install elasticsearch7
export FLASK_APP=microblog.py
export FLASK_DEBUG=1
flask run
docker inspect --format='{{.NetworkSettings.IPAddress}}' great_colden
```


# curling the elastic client

```
curl -X GET localhost:9200/_cat/nodes?v=true&pretty
curl -X GET localhost:9200/my_playlist
```


# references

https://levelup.gitconnected.com/working-with-apache-in-python-a-practical-guide-with-a-flask-app-example-cce141725633

https://www.telesens.co/2018/10/01/wrapping-app-in-webservice/

example of flask with httpd
https://www.opensourceforu.com/2023/03/deploying-a-flask-application-via-the-apache-server/

set up httpd on RHEL 8 + other detail features
https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/8/html/deploying_different_types_of_servers/setting-apache-http-server_deploying-different-types-of-servers

sample apache-vhost.conf file
https://github.com/fnep/example_fastapi_behind_apache_using_wsgi/blob/main/apache-vhost.conf

sample Docker file to load python.
https://catalog.redhat.com/software/containers/ubi8/python-311/6278e25c09f542ed990585ce?architecture=amd64&image=65cbaae5256551bfc405021a&container-tabs=dockerfile

reference to configure httpd in RHEL
https://legacy.redhat.com/pub/redhat/linux/8.0/de/doc/RH-DOCS/rhl-rg-en-8.0/s1-apache-config.html


# installing the virtualenv for app
assuming you have installed python3.6 and up

```
pip3 install virtualenv && virtualenv venv && source ./venv/bin/activate
pip3 install -r requirements.txt
deactivate
```

sometimes needs to do this.
```
sudo apt install python3-virtualenv
```

# installing the "test", cd into the test directory
```
python3 -m venv pyunit
source pyunit/bin/activate
pip3 install -r ../app/requirements.txt
pip3 install pytest coverage mockito
coverage run -m pytest ../test/ && coverage xml
deactivate
```

