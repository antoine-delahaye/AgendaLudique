FROM alpine:3.7
WORKDIR /docker-al
ADD . /docker-al
RUN apk add --no-cache uwsgi-python3 python3
RUN pip3 install --no-cache-dir --upgrade pip
RUN pip3 install --no-cache-dir wheel
RUN pip3 install --no-cache-dir -r requirements.txt
CMD [ "uwsgi", "--socket", "0.0.0.0:3031", \
               "--uid", "uwsgi", \
               "--plugins", "python3", \
               "--protocol", "uwsgi", \
               "--wsgi", "run_app:app" ]
