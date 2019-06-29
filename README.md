# Luna Lovegood Telegram bot via Telegram client API
The bot is used for HPWU International telegram group maintenance and user management.
Uses Django as RESTful service to interact with database.

## Project structure
```text
├─ .gitignore
├─ LICENSE
├─ Makefile
├─ README.md ~> This file
├─ dockerfiles/
│ └─ docker-compose.yml
├─ loony/ <~ Luna Lovegood bot itself
├─ secrets/ <~ This is part of .gitignore, create these files locally.
│ ├─ bot.env <~ *
│ ├─ django.env <~ **
│ ├─ nginx.env <~ ***
│ └─ postgresql.env <~ ****
├─ services/
│ ├─ postgresql/ <~ This should exist
│ └─ redis/ <~ This should exist
└─ spectrespecs/ <~ Django with DRF and docs.
```

#### *
```
API_ID=<Your api_id>
API_HASH=<Your api_hash>
DJANGO_PASSWORD=<Django password, create a user in Django first>
DJANGO_USER=<Django user, create a user in Django first>
TZ=<Your timezone, mine is Asia/Yekaterinburg>
```
#### **
```
C_FORCE_ROOT=true
DB_HOST=<your db hostname>
DB_NAME=<your db name>
DB_PASS=<your db user password>
DB_PORT=<your db port>
DB_USER=<your db user>
DEBUG=False
SECRET_KEY=<you django app secret key>
TZ=<Your timezone, mine is Asia/Yekaterinburg>
```
#### ***
```
TZ=<Your timezone, mine is Asia/Yekaterinburg>
```
#### ****
```
C_FORCE_ROOT=true
PGDATA=/var/lib/postgresql/data
POSTGRES_DB=<your db name>
POSTGRES_HOST=<your db hostname>
POSTGRES_PASSWORD=<your db password>
POSTGRES_PORT=<your db port>
POSTGRES_USER=<your db user>
TZ=<Your timezone, mine is Asia/Yekaterinburg>
```

## Installation
### Prerequisites
Almost any x64 `Linux` OS will do.
You will need `docker` and `docker-compose` with docker being able to start without `sudo`.

Create the files above and then type into terminal:
```bash
make install
``` 
Then lay back and relax.

## Contacts
For any reasonable questions regarding the project,
feel free to drop me a message via [Telegram](https://t.me/Spacehug)
or via [e-mail](mailto:spacehug.o0@gmail.com)