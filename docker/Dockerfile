FROM alpine

LABEL maintainer = "Antoine Delahaye"
LABEL description = "Nginx + uWSGI + Flask based on Alpine Linux and managed by Antoine Delahaye"

COPY requirements.txt /tmp/requirements.txt

RUN apk add --no-cache \
    python3 \
    bash \
    nginx \
    uwsgi \
    uwsgi-python3 \
    supervisor && \
    python3 -m ensurepip && \
    rm -r /usr/lib/python*/ensurepip && \
    pip3 install --upgrade pip setuptools && \
    pip3 install -r /tmp/requirements.txt && \
    rm /etc/nginx/conf.d/default.conf && \
    rm -r /root/.cache

COPY docker/nginx.conf /etc/nginx/
COPY docker/agenda-ludique.conf /etc/nginx/conf.d/
COPY docker/uwsgi.ini /etc/uwsgi/
COPY docker/supervisord.conf /etc/supervisord.conf

WORKDIR /docker-al
ADD . /docker-al

RUN chmod u+x docker/entrypoint.sh
ENTRYPOINT ["docker/entrypoint.sh"]
