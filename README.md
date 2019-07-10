# Luna Lovegood Telegram bot via Telegram client API
The bot is used for HPWU International telegram group maintenance and user management.
Uses Django as RESTful service to interact with database.

## Project structure and notes
```text
loony-lovegood
├── dockerfiles
│   └── docker-compose.yml
├── loony [<~ Luna Lovegood bot engine]
│   ├── project
│   │   └── settings.py
│   ├── Dockerfile
│   └── main.py
├── secrets
│   ├── bot.env [<~ Edit before use]
│   ├── django.env [<~ Edit before use]
│   ├── nginx.env [<~ Edit before use]
│   └── postgresql.env [<~ Edit before use]
├── services
│   ├── fail2ban
│   ├── nginx
│   │   ├── Dockerfile
│   │   └── nginx.conf
│   ├── ntp
│   ├── postgresql
│   │   └── dbdata [<~ Should be created beforehand]
│   └── redis
│       └── redisdata [<~ Should be created beforehand]
├── spectrespecs [<~ Django REST API on DRF]
│   ├── authentication
│   ├── core
│   ├── nightwatch
│   ├── project
│   │   ├── settings.py
│   ├── Dockerfile
│   └── manage.py
├── LICENSE
├── Makefile
└── README.md [~> This file]
```

## Installation
### Prerequisites
Almost any x64 `Linux` OS will do.
You will need `docker` and `docker-compose` with docker being able to start without `sudo`.

Edit and rename .env files in `secrets/` directory so that the names are:
```text
bot.env
django.env
nginx.env
postgresql.env
```
and then type into terminal:

```bash
make install
``` 
Press Enter, then lay back and relax.

## Contacts
For any reasonable questions regarding the project,
feel free to drop me a message via [Telegram](https://t.me/Spacehug)
or via [e-mail](mailto:spacehug.o0@gmail.com)