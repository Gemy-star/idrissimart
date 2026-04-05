# Local Development with Docker MariaDB and Redis Only

This mode runs only MariaDB and Redis in Docker.
The Django app runs directly on your host machine (macOS/Linux).

## Files used

- docker-compose.local-infra.yml
- dump.sql
- Makefile targets prefixed with infra-

## Start infrastructure

make infra-up

This starts:
- MariaDB on 127.0.0.1:3306
- Redis on 127.0.0.1:6379

## Import database dump

Option 1 (automatic on first start only):
- dump.sql is mounted to /docker-entrypoint-initdb.d/01-dump.sql
- It is imported only when MariaDB initializes a new empty volume

Option 2 (manual import any time):

make infra-db-import

## Re-import from scratch

If you need a clean re-import from dump.sql:

1. Stop and remove volumes:
   docker compose -f docker-compose.local-infra.yml down -v
2. Start again:
   make infra-up

## Useful commands

- make infra-logs
- make infra-db-shell
- make infra-redis-cli
- make infra-down

## Django settings note

manage.py defaults to idrissimart.settings.local.
That settings module is already configured for host-local services on 127.0.0.1.
