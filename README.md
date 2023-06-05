# Star Burger Food Delivery Site

This is the website of the Star Burger restaurant chain. Here you can order excellent burgers with home delivery.

![home page](./screenshots/home_ui.gif)

The example of the website is [here](https://yksb.freemyip.com/).

## Prerequisites

- Python 3.11;
- [Node.js](https://nodejs.org/en/) (v.10 or higher).

## Installation

- Download the project files.
- It is recommended to use [venv](https://docs.python.org/3/library/venv.html?highlight=venv#module-venv) for project isolation.
- Go to the root directory of the project and set up packages:

```bash
pip install -r requirements.txt
```

```bash
npm ci --dev
```

- Set up environmental variables in your operating system or in the .env file. The variables are:

  - `SECRET_KEY` - a secret key for a particular Django installation (obligatory);
  - `DEBUG` - a boolean that turns on/off debug mode (optional, `True` by default);
  - `LANGUAGE_CODE` - a string representing the language code for this installation (optional, `ru-RU` by default);
  - `TIME_ZONE` - a string representing the time zone for this database connection(optional, `UTC` by default);
  - `YA_API_KEY` - your YANDEX API key (obligatory, go to [the develop cabinet](https://developer.tech.yandex.ru/) for more);
  - `ALLOWED_HOSTS` - a list of strings representing the host/domain names that this Django site can serve (optional, `localhost,127.0.0.1` by default);
  - `ROLLBAR_ON` - a boolean that turns on/off [rollbar.com tracking platform](https://rollbar.com/) (optional, `False` by default)
  - `ROLLBAR_POST_SERVER_ITEM_ACCESS_TOKEN` - a token to set an error report to the [rollbar.com tracking platform](https://rollbar.com/) (obligatory only in the case when `ROLLBAR_ON` is `True`);
  - `ROLLBAR_ENVIRONMENT` - a string that describes the current environment, for example `development` or `production` (optional, `development` by default). It is used in an error report to the [rollbar.com tracking platform](https://rollbar.com/);
  - `DATABASE_URL` - a database URL, see [URL schema](https://github.com/jazzband/dj-database-url#url-schema) for more (obligatory)

To set up variables in .env file, create it in the root directory of the project and fill it up like this:

```bash
SECRET_KEY=replace_me
DEBUG=True
LANGUAGE_CODE=en-us
TIME_ZONE=Europe/Moscow
YA_API_KEY=replace_me
ALLOWED_HOSTS=localhost,127.0.0.1
ROLLBAR_ON=True
ROLLBAR_POST_SERVER_ITEM_ACCESS_TOKEN=replace_me
ROLLBAR_ENVIRONMENT=development
DATABASE_URL=postgres://USER:PASSWORD@HOST:PORT/BASE_NAME
```

- Create SQLite database:

```bash
python manage.py migrate
```

- Create a superuser:

```bash
python manage.py createsuperuser
```

## Start

- Run a development server:

```bash
python manage.py runserver
```

- Run a frontend:

```bash
./node_modules/.bin/parcel watch bundles-src/index.js --dist-dir bundles --public-url="./"
```

- Go to [the admin site](http://127.0.0.1:8000/admin/) and fill the base;
- Go to [the home page](http://127.0.0.1:8000/).

## Updating the code on the server

Run:

```bash
./deploy
```

## Interfaces

### Home page

On [the home (public) page](http://127.0.0.1:8000/), a user can choose dishes and submit an order.

### Manager interface

On [the service (manager) page](http://127.0.0.1:8000/manager/orders/), a manager sees uncompleted orders, restaurants that can fulfill each order, distances between a restaurant and a place of delivery. Right from here the manager can go to a card of an order in the admin site, edit the order and return by clicking the "Save" button. If the manager chooses a restaurant for the order, the order's status will be changed automatically.

![manager UI](./screenshots/manager_ui.gif)

### Browsable API interface

A developer can use [the browsable API interface](http://127.0.0.1:8000/api/order/). It's possible to test order acceptance process here:

- Put JSON text into the "Content" field, for example:

```json
{"address": "г. Москва, ул. Твардовского, д. 4, к. 1, кв. 16",
 "firstname": "Стелла",
 "lastname": "Дроздова",
 "phonenumber": "+9607994512",
 "products": [{"product": 1, "quantity": 2},
              {"product": 2, "quantity": 1},
              {"product": 3, "quantity": 1}]}
```

- Press "POST".

![browsable API](./screenshots/developer_ui.gif)

## Project goals

The project was created for educational purposes.
It's a lesson for python and web developers at [Devman](https://dvmn.org).
