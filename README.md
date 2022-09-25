# Currency converter

Light Django app with currency integration [Yahoo!Ⓡ finance](https://finance.yahoo.com).
- App uses celery for reload currency rates for previously added currencies;
- Celery beat run periodically load_currency_rates task for update rates;
- New currencies can be added via management command `load_currency_rate` (see below);
- Endpoint: `/api/currency/` shows all available currencies with available rates;
- Endpoint: `/api/currency/PLN/EUR/` allows to convert currencies. In this case PLN to EUR;
- API doc is available at: `/api/docs/` You can find available filters

[![Black code style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)


<table border=1 cellpadding=10><tr><td>

#### \*\*\* IMPORTANT LEGAL DISCLAIMER \*\*\*

---

**Yahoo!, Y!Finance, and Yahoo! finance are registered trademarks of
Yahoo, Inc.**

project dependency yfinance is **not** affiliated, endorsed, or vetted by Yahoo, Inc. It's
an open-source tool that uses Yahoo's publicly available APIs, and is
intended for research and educational purposes.

**You should refer to Yahoo!'s terms of use**
([here](https://policies.yahoo.com/us/en/yahoo/terms/product-atos/apiforydn/index.htm),
[here](https://legal.yahoo.com/us/en/yahoo/terms/otos/index.html), and
[here](https://policies.yahoo.com/us/en/yahoo/terms/index.htm)) **for
details on your rights to use the actual data downloaded. Remember - the
Yahoo! finance API is intended for personal use only.**

</td></tr></table>

---


## Settings

Base startup settings are in ./.envs/.local/ directory. Please use it only locally.
With production use you have to use environment variables and settings from production.py


## Local development using Docker
Project support local development via docker-compose.
Docker-compose contain django, redis, mysql, celery and celery beat containers. To build and run use below commands:

    $ docker-compose -f local.yml build
    $ docker-compose -f local.yml up

For better quality before first work please enable pre-commit:

    $ pre-commit install

## Basic Commands

### Loading data from provider

-   To load new currencies EUR and PLN use command:

        $ python manage.py load_currency_rate EUR PLN --period 5d

    Available periods: `1d`, `5d`, `1mo`, `3mo`, `6mo`, `1y`, `2y`, `5y`, `10y`, `ytd`, `max`

### Type checks

Running type checks with mypy:

    $ mypy

### Running tests with pytest

    $ pytest

### Sentry

Sentry is an error logging service. You can sign up for a free account at <https://sentry.io/signup/> or download and host it yourself.
The system is set up with reasonable defaults, including 404 logging and integration with the WSGI application.

You must set the DSN url in production.

## Deployment

Needs information
