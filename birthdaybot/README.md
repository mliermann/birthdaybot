# README for birthdaybot.py

## Description
`birthdaybot.py` implements an API to allow users to add their birthdays to a data store, and to receive a birthday
greeting when appropriate.

## Requirements
* Python 3
* Flask (`pip install flask`)
* SQLAlchemy (`pip install sqlalchemy`)

The test scripts in `tests.py` additionally require the Faker library (`pip install faker`).

Faker is a library to generate realistic dummy data - more info at https://faker.readthedocs.io/en/master/

## Usage
Run the script with `python birthdaybot.py` or `./birthdaybot.py` if you have made it executable.

The program uses the following environment variables:
* `BDB_DB_USER`: user name for MySQL connection
* `BDB_DB_PASS`: password for the above user
* `BDB_DB_NAME`: name of database to use - must be one the specified user has read/write permissions on
* `BDB_DB_HOST`: host name for MySQL server
* `BDB_DB_PORT`: port MySQL is running on (usually 3306)

No default values are assumed for the above if they are not supplied. Note that the program **will not work** if these
environment variables are not set using the `export` command or a similar mechanism.

## Functionality
The program exposes API endpoints as follows:
* `PUT /hello/<username>`: accepts a request with body `{ "dateOfBirth": "YYYY-MM-DD" }`. Inserts or updates this data
in the database. Request body can be supplied either as a JSON document, as form data, or as query parameters appended
to the URL - the endpoint can process all three. Dates in the future are rejected with an appropriate message and a
400 HTTP status code.
* `GET /hello/<username>`: checks whether the specified user's birth date is found in the database; returns a HTTP 400
status code and error message if the user is not found in the database, otherwise returns a 200 OK response and a
message either wishing the user a happy birthday, or giving the days to the user's next birthday

## Limitations, concerns, possible improvements
* all user names are converted to lowercase before being inserted into the database
* no protection is in place to prevent data from being overwritten - this is by design, as this behaviour was
requested in the spec
* user names must be alphabet characters *only*
