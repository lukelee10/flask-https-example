# set by Jenkinsfile(.annex,.ms)
#  https://catalog.redhat.com/software/containers/ubi8/python-311/6278e25c09f542ed990585ce?architecture=amd64&image=65cbaae5256551bfc405021a&container-tabs=overview
FROM docker.artifactory.code.dodiis.mil/dpaas/ubi8-ccp:8.9


# image build time

ARG AWS_DEFAULT_REGION
ARG KEYCLOAK_AUTHENTICATION_URL

# container run time
ENV AWS_DEFAULT_REGION $AWS_DEFAULT_REGION
ENV KEYCLOAK_AUTHENTICATION_URL $KEYCLOAK_AUTHENTICATION_URL

#     #PIP_INDEX_URL=http://pypi.appdev.proj.abc.de.fgh/simple/ \
#     #PIP_TRUSTED_HOST=pypi.appdev.proj.abc.de.fgh \
#     PIP_DOWNLOAD_CACHE=/tmp

# USER apache
# WORKDIR ${WORKDIR}

# configure OS and install python3.11 through yum
RUN INSTALL_PKGS="python3.11-pip python3.11-mod_wsgi vim-enhanced procps httpd" && \
    yum -y module enable  httpd:2.4 && \
    yum -y --setopt=tsflags=nodocs install $INSTALL_PKGS && \
    rpm -V $INSTALL_PKGS && \
    # Remove redhat-logos-httpd (httpd dependency) to keep image size smaller.
    rpm -e --nodeps redhat-logos-httpd && \
    yum -y clean all --enablerepo='*'


# USER ${DOCKER_USER}
# copy code from current directory to work directory
COPY app/requirements.txt /var/www/smart/app/
COPY app /var/www/smart/app/
COPY config/smart.wsgi /var/www/wsgi-scripts/

# Add the apache VirtualHost, to setup the WSGI module for the app
COPY config/httpd.conf /etc/httpd/conf/
COPY config/apache-vhost.conf /etc/httpd/conf.d/vhost.conf

WORKDIR /var/www/smart/app/

RUN chown -R apache:apache /var/www/smart \
    && chown -R apache:apache /var/www/wsgi-scripts \
    && chown -R apache:apache /var/log/httpd \
    && chown -R apache:apache /var/run/httpd \
    && chown -R apache:apache /etc/httpd \
    && chown -R apache:apache /usr/share/httpd

# Optional: Redirect error log to stdout, to make it visible in `docker compose up` output
# ---RUN ln -sf /dev/stdout /var/log/httpd/error_log

EXPOSE 8080

RUN pip3 install virtualenv

USER apache
# install dependencies under virtual environment: https://docs.python.org/3/library/venv.html
# RUN pip3 install --user virtualenv \
#     && python3 -m venv env
# RUN python3 -m pip install virtualenv && \
RUN  virtualenv venv \
     && source ./venv/bin/activate

RUN python3 -m pip install -r requirements.txt

# RUN source env/bin/activate \
#     && pip3 install -r requirements.txt
    # && chown -hR ${UID}:${GID} /opt/rh/rh-${PYTHON_DIR}/root/usr/bin/${PYTHON_DIR} \
    # && chown -hR ${UID}:${GID} /opt/rh/rh-${PYTHON_DIR}/root/usr/local/bin/gunicorn \
    # && setcap 'cap_net_bind_service=+ep' /opt/rh/rh-${PYTHON_DIR}/root/usr/bin/${PYTHON_DIR} \
    # && setcap 'cap_net_bind_service=+ep' /opt/rh/rh-${PYTHON_DIR}/root/usr/local/bin/gunicorn

# ENV VIRTUAL_ENV=$WORKDIR/env
# ENV PATH="$VIRTUAL_ENV/bin:$PATH"
# CMD ["gunicorn", "-w", "4", "-b", ":8443", \
#     "--certfile", "./certs/internalClient.pem", \
#     "--keyfile", "./certs/internalClient.key", \
#     "app:app" \
# ]

CMD ["httpd", "-D", "FOREGROUND"]
