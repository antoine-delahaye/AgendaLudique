FROM python:3.9.1-slim
WORKDIR /docker-al
ADD . /docker-al
RUN pip install -r requirements.txt
EXPOSE 56733
CMD ["python3", "run_app.py"]
