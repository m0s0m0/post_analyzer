# Use the official Python 3.11 Alpine image as a parent image
FROM python:3.11-alpine

# Set environment variables
ENV PYTHONUNBUFFERED 1

RUN mkdir /app

WORKDIR /app

RUN apk update \
  && apk add  gcc python3-dev musl-dev libffi-dev openssl-dev libcurl curl-dev libevent-dev build-base \
    cargo

# Copy the requirements file into the container at /app
COPY ./requirements/local.txt ./requirements.txt

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY ./start_app.sh ./start_app.sh

# Copy the current directory contents into the container at /app
COPY . /app/

# Expose port 8000 for Gunicorn
EXPOSE 8000


ENTRYPOINT [ "sh", "./start_app.sh" ]
# CMD ["gunicorn", "post_analyzer.wsgi:application", "--bind", "0.0.0.0:8000"]
