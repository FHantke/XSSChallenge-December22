# XSS Challenge - December 22
This repository contains the code and the intended solution for the December XSS challenge of Intigriti's monthly challenge.

## Difficulty
The challenge difficulty depends on your settigns inside of `docker-compose.yml` and can be set to either `medium` or `hard`.
For the monthly challenge, we choose to set the difficulty to medium.
However, the challenge also contained an unintended solution which made it very easy to solve (read the writeups below).

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

There are also a couple of writeups from the community for the intended and unintended solution:
* https://blog.effectrenan.com/intigriti-december-xss-challenge-1222/
* https://jorenverheyen.github.io/intigriti-december-2022.html
* https://github.com/oddrabbit/Intigriti-challenge-1222-Solution/blob/main/main.md
* https://www.youtube.com/watch?v=FowbZ8IlU7o
