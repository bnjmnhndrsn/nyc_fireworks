install virtualenv

create virtualenv and call it nyc_fireworksenv

install Postgres.app

in postgres:

```
CREATE DATABASE nyc_fireworks_dev;
```

add this to end of nyc_fireworksenv/bin/activate:
```
export DATABASE_URL=postgres://:@localhost/nyc_fireworks_dev
export DEBUG=True
```
