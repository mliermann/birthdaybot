# set base image
FROM python:3.9-slim-buster

# set working directory in container
WORKDIR /app

# copy dependencies file to workdir
COPY requirements.txt .

# install dependencies listed in requirements.txt
RUN pip install -r requirements.txt

# copy contents of script directory into workdir
COPY birthdaybot/ .

# command to run on container start
CMD [ "python", "./birthdaybot.py" ]