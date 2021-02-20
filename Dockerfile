FROM alpine:latest
WORKDIR /docker-al
ADD . /docker-al
RUN apk add --no-cache python3 py3-pip uwsgi-python3
RUN pip3 install --no-cache-dir --upgrade pip
RUN pip3 install --no-cache-dir wheel
RUN pip3 install --no-cache-dir -r requirements.txt
EXPOSE 80
CMD ["python3", "run_app.py"]
