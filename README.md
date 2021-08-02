# README for the birthdaybot package

This is a WIP. When completed, it will consist of the following:
* birthdaybot/birthdaybot.py: Python3 web service
* birthdaybot/tests.py: tests for the above
* Dockerfile: to build a Docker image from birthdaybot
* GCS deployment files: to deploy the birthdaybot Docker image to GKE
* dbcreate.sql: MySQL database creation script
* architecture diagrams

---

## Original spec
* Design and code a simple "Hello World" application that exposes the following
HTTP-based APIs:

**Description:** Saves/updates the given user’s name and date of birth in the database.

*Request:* `PUT /hello/<username> { “dateOfBirth”: “YYYY-MM-DD” }`

*Response:* `204 No Content`

Note:

`<username>` must contain only letters.

`YYYY-MM-DD` must be a date before the today date.

**Description:** Returns hello birthday message for the given user

*Request:* `GET /hello/<username>`

*Response:* `200 OK`

*Response Examples:*

A. If username’s birthday is in N days:

`{ “message”: “Hello, <username>! Your birthday is in N day(s)”}`

B. If username’s birthday is today:
`{ “message”: “Hello, <username>! Happy birthday!” }`

Note: Use storage/database of your choice.

---
* Produce a system diagram of your solution deployed to either AWS or GCP (it's not
required to support both cloud platforms).
---
* Write configuration scripts for building and no-downtime production deployment of
this application, keeping in mind aspects that an SRE would have to consider.
---

# To Do MSL:

* GCloud Run YAML definition
* GCloud SQL setup doc
* test GCloud deploy
* container build instructions to GCR
* architecture diagram
* also mention differences if deploying to GKE
* swap in gUnicorn instead of Flask?