#!/usr/bin/python
#
# birthdaybot.py:   web service to dispense birthday greetings
#                   Michael Liermann (michael.liermann.72@gmail.com), August 2021

import datetime
import logging
import os
import sys

from flask import Flask, request, jsonify
import sqlalchemy

OK = "OK"
ERR = "ERR"
ERR_NOT_FOUND = "404"

# define global app context
app = Flask(__name__)

### set up global logger
# first see if we have an env var set to define log level
try:
    bb_loglevel = os.environ["BDB_LOGLEVEL"]
except Exception as e:
    bb_loglevel = "WARNING"
# set log level based on environment variable, or use default of WARNING
if bb_loglevel == "DEBUG":
    logging.basicConfig(level=logging.DEBUG)
elif bb_loglevel == "INFO":
    logging.basicConfig(level=logging.INFO)
elif bb_loglevel == "WARNING":
    logging.basicConfig(level=logging.WARNING)
elif bb_loglevel == "ERROR":
    logging.basicConfig(level=logging.ERROR)
elif bb_loglevel == "CRITICAL":
    logging.basicConfig(level=logging.CRITICAL)

logger = logging.getLogger()


def initDbConnection():
    """
    initialiase DB connection based on environment variables
    :return: DB connection object, or error
    """
    try:
        db_user = os.environ["BDB_DB_USER"]
        db_pass = os.environ["BDB_DB_PASS"]
        db_name = os.environ["BDB_DB_NAME"]
        db_host = os.environ["BDB_DB_HOST"]
        db_port = os.environ["BDB_DB_PORT"]
    except Exception as e:
        logger.critical("could not parse environment for DB connection parameters")
        return ERR
    db_config = {
        "pool_size": 5,
        "max_overflow": 2,
        "pool_timeout": 30,
        "pool_recycle": 1800
    }
    logger.info("attempting MySQL connection to %s:%s" % (db_host, db_port))
    logger.debug("connection parameters: DB name %s, DB user %s" % (db_name, db_user))
    logger.debug("connection config: %s" % db_config)
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
        logger.critical("could not connect to DB - %s" % e)
        return ERR
    logger.info("connection established to MySQL server at %s:%s" % (db_host, db_port))
    return dbConn


# create global DB handle here so that it is available throughout
db = initDbConnection()
if db == ERR:
    logger.critical("unable to establish DB connection - aborting")
    sys.exit(1)


@app.before_first_request
def createDbTables():
    """
    create required database table if it does not already exist
    :param dbHandle: DB connection object
    :return: OK or ERR
    """
    logger.info("creating required DB table if it does not already exist")
    try:
        with db.connect() as conn:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS birthdays "
                "( username VARCHAR(255) NOT NULL, birthday DATE NOT NULL, "
                "PRIMARY KEY (username) );"
            )
        return OK
    except Exception as e:
        logger.info("Error creating table: %s" % e)
        return ERR


def dbWrite(dbData):
    """
    write data to DB
    :param dbHandle: DB connection object
    :param dbData: data to insert into DB
    :return: OK or ERR
    """
    insUser = dbData[0]
    insDate = dbData[1]
    print(insUser, insDate)
    sqlStmt = sqlalchemy.text("INSERT INTO birthdays (username, birthday)" "VALUES (:insUser, :insDate)"
                              "ON DUPLICATE KEY UPDATE username = VALUES(username), birthday = VALUES(birthday)")
    try:
        with db.connect() as conn:
            conn.execute(sqlStmt, insUser=insUser, insDate=insDate)
    except Exception as e:
        logger.exception(e)
        # add Flask Response and 500 HTTP status here
        return ERR
    logger.debug("successfully wrote dataset %s, %s to database" % (insUser, insDate))
    return OK


def dbQuery(username):
    """
    query DB for birthday information for specified username
    :param dbHandle: DB connection object
    :param username: value to query DB for
    :return: birthdate as YYYY-MM-DD format string, or ERR_NOT_FOUND
    """
    logger.debug("querying database for birth date for user %s" % username)
    sqlStmt = sqlalchemy.text("SELECT birthday FROM birthdays WHERE username = :username")
    try:
        with db.connect() as conn:
            res = conn.execute(sqlStmt, username=username)
            # we use fetchone() below because we will only ever have one result
            #rescount = res.rowcount
            if int(res.rowcount) > 0:
                logger.debug("retrieved birth date for user %s" % username)
                return res.fetchone()["birthday"]
            else:
                logger.debug("no birth date found for user %s" % username)
                return ERR_NOT_FOUND
    except Exception as e:
        # note we should not see this exception unless the database went away mid-query
        logger.exception(e)
        logger.info("DB query failed for unexpected reasons")
        # add Flask Response and 500 HTTP status here
        return ERR


def calcDays(dateToCheck):
    """
    returns full days remaining from today's date until dateToCheck
    :param dateToCheck: date to calculate days to, datetime.date format YYYY-MM-DD
    :return: integer
    """
    today = datetime.date.today()
    # guard against *somehow* receiving an incorrect data type
    if type(dateToCheck) is not datetime.date:
        origBirthday = datetime.date.fromisoformat(str(dateToCheck))
    else:
        origBirthday = dateToCheck
    # determine the next birthday for this date of birth
    nextBirthday = datetime.date(today.year, origBirthday.month, origBirthday.day)
    # calculate days to next birthday
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


@app.route("/hello/<username>", methods=["PUT"])
def addUser(username):
    """
    add user data to database if it passes checks
    :param username: user name supplied as part of request URL
    :return: 204 No Content response, or an error
    """
    logger.debug("attempting to add user %s to database" % username)
    if not str(username).isalpha():
        logger.info("rejecting user name %s: incorrect format" % username)
        return "Parameter 'username' must be alphabetic characters only", 400
    logger.debug("supplied user name passes validity check")
    if request.json:
        req=request.get_json()
    elif request.args:
        req = request.args
    else:
        req=request.form
    # now we have request data, regardless of whether we received it as JSON, as form data, or appended to the URL
    # extract the data field we need, return an error if it's not there
    try:
        userDob = req["dateOfBirth"]
    except Exception as e:
        logger.error(e)
        return "invalid data", 400
    logger.debug("date of birth supplied is %s" % userDob)
    # validate the supplied date of birth - step 1: is it a proper ISO format date?
    try:
        thisDob = datetime.datetime.strptime(userDob, "%Y-%m-%d")
        thisDob = thisDob.date()
    except Exception as e:
        logger.info("rejecting birth date %s: incorrect format" % userDob)
        return "Data supplied is not valid date", 400
    # next, check that supplied date of birth is before today's date
    today = datetime.date.today()
    if thisDob > today:
        logger.info("rejecting birth date %s: it is in the future" % thisDob)
        return "Date supplied is in the future, thus not a valid date", 400
    logger.debug("birth date supplied has passed validity checks")
    # assemble data & send to dbWrite function - ensure user name is all lowercase when stored
    userData = [str(username).lower(), thisDob]
    logger.debug("writing dataset %s, %s to database" % (userData[0], userData[1]))
    writeRes = dbWrite(userData)
    if writeRes == OK:
        return "No Content", 204
    else:
        return "error writing to database", 500


@app.route("/hello/<username>", methods=["GET"])
def checkUser(username):
    """
    retrieve date of birth for specified user and check if birthday
    :param username: user name supplied as part of request URL
    :return: 200 OK plus a message
    """
    if not str(username).isalpha():
        logger.info("rejecting user name %s: incorrect format" % username)
        return "Parameter 'username' must be alphabetic characters only", 400
    # convert user name to lower case before DB query
    thisUser = str(username).lower()
    userBday = dbQuery(thisUser)
    if userBday == ERR_NOT_FOUND:
        logger.info("no birth date found in DB for user %s" % username)
        return "no birth date found in DB for user %s" % username, 400
    # now we have a date of birth for this user - let's check when the birthday is
    daysLeft = calcDays(userBday)
    # construct reponse JSON object
    if daysLeft == 0:
        logger.info("wished %s a happy birthday" % username)
        resp = {"message": "Hello, %s! Happy birthday!" % username}
    else:
        resp = {"message": "Hello, %s! Your birthday is in %s day(s)" % (username, daysLeft)}
    # return JSON response and 200 HTTP status
    return jsonify(resp), 200


if __name__ == "__main__":
    logger.info("starting Flask app")
    app.run(host="0.0.0.0", port=8080, debug=False)