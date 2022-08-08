# XSS Challenge
This XSS challenge is a proposal for the monthly Intigriti XSS challenge.

## Setup
Everything you need to setup the challenge is inside the challenge directory. You can use docker to start it:
```
docker-compose up
```

In case of issues with the `psycopg2` package on M1 Macs, try the [following](https://stackoverflow.com/questions/62807717/how-can-i-solve-postgresql-scram-authentication-problem):
```export DOCKER_DEFAULT_PLATFORM=linux/amd64```

## Goal
The goal is to `alert` the victims' username.
Your payload should work in the latest version of Chrome and FireFox.
It should also not require any kind of user interaction except the user clicking on your malicious URL.

## Solution
The intended solution and an explination is inside the solution directory.
__DO NOT SPOILER YOURSELF!__
