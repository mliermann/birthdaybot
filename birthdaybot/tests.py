#!/usr/bin/python

import datetime
import logging
import os
from faker import Faker

from flask import Flask, render_template, request, Response
import sqlalchemy

OK = "OK"
ERR = "ERR"
ERR_NOT_FOUND = "404"

def testDateLogic():
    """
    generate & check some fake dates to confirm that calcDays() works as intended
    :return: OK
    """
    for z in range(10):
        thisDate = Faker().date()
        #print(thisDate, type(thisDate))
        dateRange = calcDays(thisDate)
        print("Days until %s: %s" % (str(thisDate), str(dateRange)))
        # TODO: fix the wording / output of the above, if leaving it in at all
    return OK


def makeFakeData(numRecords=20):
    """
    generate specified number of fake datasets
    :param numRecords: number of datasets to generate
    :return: list of tuples
    """
    myData = []
    for z in range(numRecords):
        fakeName = Faker().name()
        fakeBirthdate = Faker().date()
        fakeUser = fakeName.split()[0].lower() + fakeName.split()[1].lower()
        thisRecord = (fakeUser, fakeBirthdate)
        myData.append(thisRecord)
    return myData


def initData():
    """
    initialise DB connection, DB tables, and insert some dummy data
    :return: OK or ERR
    """
    dbConn = initDbConnection()
    createDbTables(dbConn)
    dummyData = makeFakeData(50)
    for z in range(50):
        dbWrite(dbConn, dummyData[z])
    return OK