FROM python:3.13.7
WORKDIR /app
COPY requirements.txt /app
RUN --mount=type=cache,target=/root/.cache/pip pip3 install -r requirements.txt
