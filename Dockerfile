FROM python:3.11-slim
WORKDIR /workspace
COPY . /workspace
RUN pip install -r flaskApp/requirements.txt
EXPOSE 5000
WORKDIR /workspace/flaskApp
CMD gunicorn --bind 0.0.0.0:${PORT:-5000} app:app
