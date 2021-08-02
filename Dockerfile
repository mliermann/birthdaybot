FROM python:3

RUN pip install flask
RUN pip install faker
RUN pip install sqlalchemy

ADD birthdaybot/birthdaybot.py /
ADD birthdaybot/tests.py /

CMD [ "python", "./birthdaybot.py" ]