#!/usr/bin/python
#
# birthdaybot.py:   web service to dispense birthday greetings
#                   Michael Liermann (michael.liermann.72@gmail.com), August 2021

import datetime
import logging
import os

from flask import Flask, render_template, request, Response
import sqlalchemy

OK = "OK"
ERR = "ERR"
ERR_NOT_FOUND = "404"

app = Flask(__name__)

logger = logging.getLogger()


def initDbConnection():
    """
    initialiase DB connection based on environment variables
    :return: DB connection object, or error
    """
    db_user = os.environ["BDB_DB_USER"]
    db_pass = os.environ["BDB_DB_PASS"]
    db_name = os.environ["BDB_DB_NAME"]
    db_host = os.environ["BDB_DB_HOST"]
    db_port = os.environ["BDB_DB_PORT"]
    db_config = {
        "pool_size": 5,
        "max_overflow": 2,
        "pool_timeout": 30,
        "pool_recycle": 1800
    }
    try:
        dbConn = sqlalchemy.create_engine(
            sqlalchemy.engine.url.URL.create(
                drivername="mysql+pymysql",
                username=db_user,
                password=db_pass,
                host=db_host,
                port=db_port,
                database=db_name
            ),
            **db_config
        )
    except Exception as e:
        logger.critical("Could not connect to DB - %s" % e)
        return ERR
    return dbConn


def createDbTables(dbHandle):
    """
    create required database table if it does not already exist
    :param dbHandle: DB connection object
    :return: OK or ERR
    """
    try:
        with dbHandle.connect() as conn:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS birthdays "
                "( username VARCHAR(255) NOT NULL, birthday DATE NOT NULL, "
                "PRIMARY KEY (username) );"
            )
        return OK
    except Exception as e:
        logger.info("Error creating table: %s" % e)
        return ERR


def dbWrite(dbHandle, dbData):
    """
    write data to DB
    :param dbHandle: DB connection object
    :param dbData: data to insert into DB
    :return: OK or ERR
    """
    insUser = dbData[0]
    insDate = dbData[1]
    sqlStmt = sqlalchemy.text("INSERT INTO birthdays (username, birthday)" "VALUES (:insUser, :insDate)"
                              "ON DUPLICATE KEY UPDATE username = VALUES(username), birthday = VALUES(birthday)")
    try:
        with dbHandle.connect() as conn:
            conn.execute(sqlStmt, insUser=insUser, insDate=insDate)
    except Exception as e:
        logger.exception(e)
        # add Flask Response and 500 HTTP status here
        return ERR
    return OK


def dbQuery(dbHandle, username):
    """
    query DB for birthday information for specified username
    :param dbHandle: DB connection object
    :param username: value to query DB for
    :return: birthdate as YYYY-MM-DD format string, or ERR_NOT_FOUND
    """
    sqlStmt = sqlalchemy.text("SELECT birthday FROM birthdays WHERE username = :username")
    try:
        with dbHandle.connect() as conn:
            res = conn.execute(sqlStmt, username=username)
            # we use fetchone() below because we will only ever have one result
            rescount = res.rowcount
            if int(rescount) > 0:
                return res.fetchone()
            else:
                return ERR_NOT_FOUND
    except Exception as e:
        logger.exception(e)
        # add Flask Response and 500 HTTP status here
        return ERR
    return OK


def calcDays(dateToCheck):
    """
    returns full days remaining from today's date until dateToCheck
    :param dateToCheck: date to calculate days to, datetime.date format YYYY-MM-DD
    :return: integer
    """
    today = datetime.date.today()
    origBirthday = datetime.date.fromisoformat(dateToCheck)
    nextBirthday = datetime.date(today.year, origBirthday.month, origBirthday.day)
    if today<nextBirthday:
        daysLeft = (nextBirthday - today).days
        return daysLeft
    elif today == nextBirthday:
        daysLeft = 0
        return daysLeft
    else:
        newDate = datetime.date(nextBirthday.year + 1, nextBirthday.month, nextBirthday.day)
        daysLeft = (newDate - today).days
        return daysLeft
    return OK

