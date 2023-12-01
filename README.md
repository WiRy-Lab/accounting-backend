# Django Accounting App

## Development

### Setup

1. Install [Docker](https://docs.docker.com/install/)
2. Clone this repository
3. Run `docker-compose up -d` to start MySQL Server
4. Open web browser and go to `http://localhost:8080/` you should see phpMyAdmin
5. Install Python 3.11
6. Install poetry `pip install poetry`
7. Install dependencies `poetry install`
8. Run `poetry shell` to activate virtual environment
9. Run `python manage.py migrate` to create database tables
10. Run `python manage.py runserver` to start development server
