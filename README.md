# Star Burger Food Delivery Site

This is the website of the Star Burger restaurant chain. Here you can order excellent burgers with home delivery.

![home page](./screenshots/home_ui.gif)

The example of the website is [here](https://yksb.freemyip.com/).

## Prerequisites

- Python 3.11;
- [Docker Desktop](https://docs.docker.com/desktop/) or
- [Docker Engine](https://docs.docker.com/engine/install/) and [the Compose plugin](https://docs.docker.com/compose/install/linux/);

The project was tested with Docker version 23.0.5 and Docker Compose version v2.17.3

## Installation

- Download the project files;
- Go to the root directory of the project;
- Set up environmental variables in the .env file. The variables are:

  - `SECRET_KEY` - a secret key for a particular Django installation (obligatory);
  - `DEBUG` - a boolean that turns on/off debug mode (optional, `True` by default);
  - `LANGUAGE_CODE` - a string representing the language code for this installation (optional, `ru-RU` by default);
  - `TIME_ZONE` - a string representing the time zone for this database connection(optional, `UTC` by default);
  - `YA_API_KEY` - your YANDEX API key (obligatory, go to [the develop cabinet](https://developer.tech.yandex.ru/) for more);
  - `ALLOWED_HOSTS` - a list of strings representing the host/domain names that this Django site can serve (optional, `localhost,127.0.0.1` by default);
  - `ROLLBAR_ON` - a boolean that turns on/off [rollbar.com tracking platform](https://rollbar.com/) (optional, `False` by default)
  - `ROLLBAR_POST_SERVER_ITEM_ACCESS_TOKEN` - a token to set an error report to the [rollbar.com tracking platform](https://rollbar.com/) (obligatory only in the case when `ROLLBAR_ON` is `True`);
  - `ROLLBAR_ENVIRONMENT` - a string that describes the current environment, for example `development` or `production` (optional, `development` by default). It is used in an error report to the [rollbar.com tracking platform](https://rollbar.com/);
  - `DATABASE_URL` - a database URL, see [URL schema](https://github.com/jazzband/dj-database-url#url-schema) for more (obligatory);
  - `POSTGRES_PASSWORD` is required for you to use the PostgreSQL image (obligatory), go to the [Docker hub](https://hub.docker.com/_/postgres) for more;
  - `CSRF_TRUSTED_ORIGINS` is required for admin site correct work (go [here](https://stackoverflow.com/questions/71319284/django-admin-panel-deploy-on-server-forbidden-403-csrf-verification-failed-re) for more);

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
POSTGRES_PASSWORD=replace_me
CSRF_TRUSTED_ORIGINS=http://localhost
```

### Development installation

Build the images and run the app stack:

```bash
docker compose -f compose-dev.yaml up -d --build
```

### Adding a superuser

- Find out the `backend-dev` container id:

```bash
docker ps | grep backend-dev
```

- Create a superuser:

```bash
docker exec -it {container_id} python manage.py createsuperuser
```

### Usage

- Go to [the admin site](http://127.0.0.1:8000/admin/) and fill the base;
- Go to [the home page](http://127.0.0.1:8000/).

## Interfaces

### Admin site

Go to [the admin site](http://127.0.0.1:8000/admin/) and fill the base;

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

## Debugging with VSCode

Add a launch configuration to the `.vscode/launch.json` file:

```json
{
  "configurations": [
    {
      "name": "Python: Remote Attach",
      "type": "python",
      "request": "attach",
      "port": 5678,
      "host": "localhost",
      "pathMappings": [
        {
          "localRoot": "${workspaceFolder}",
          "remoteRoot": "/app"
        }
      ]
    }
  ]
}
```

To debug , run:

```bash
docker compose -f compose-debug.yaml up -d --build
```

To debug with hot reloading, run:

```bash
docker compose -f compose-debug-reload.yaml up -d --build
```

Press `F5` to start debugging.

_Note_: when debugging with hot reloading, uncheck the `Uncaught Exceptions` flag on the `Run and Debug` panel. This can help to avoid the annoing `Exception has occurred: SystemExit` message each time when you save an app file.

To find out more about debugging in Docker containers, see the VSCode documentation:

- [Debug Python within a container](https://code.visualstudio.com/docs/containers/debug-python);
- [Debug Python with Docker Compose](https://code.visualstudio.com/docs/containers/docker-compose#_python);
- [How to enable hot reloading in Django or Flask apps](https://code.visualstudio.com/docs/containers/debug-python#_how-to-enable-hot-reloading-in-django-or-flask-apps);

## Project goals

The project was created for educational purposes.
It's a lesson for python and web developers at [Devman](https://dvmn.org).
