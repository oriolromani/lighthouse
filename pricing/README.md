# Lighthouse technical challenge Oriol Romani Picas
This is a Django app that contains a management command to parse and insert meter readings data from meD0010 format files into a local SQLite3 DB. The app provides an adming interface with some searching functionalities.

## Usage

1. Install Python 3 if you haven't already. You can download it from the [official Python website](https://www.python.org/downloads/).

2. Install the required dependencies using pip, it is recommended to use a [virtual environment](https://docs.python.org/3/library/venv.html) for this. Run the following with the env activated:

```pip install -r requirements.txt```

3. Migrate into DB

```python manage.py migrate```

4. Create superuser

```python manage.py createsuperuser```

Follow the prompts create a user that can access admin interfaces

5. Set env variables

Create a .env file and set the following variables. For this you would need first to create a [Google Big Table DB](https://cloud.google.com/bigtable?hl=es)

6. Run the server

```python manage.py runserver```

The functionality would be available on [http://localhost:8000/api/pricing/pre_corona_difference/](http://localhost:8000/api/pricing/pre_corona_difference/)

7. Running tests

Some tests are provided, that can be run like:

```python manage.py test```

## Improvements

- Use MySQl as a databse for the exchange rates instead of the default SQLite DB
