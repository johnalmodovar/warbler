# Warbler

A Twitter clone project.

## Stack

![alt text](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![alt text](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)
![alt text](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)

## Deployed Page

https://warbler.johnalmodovar.com/

## Run Locally

#### From main directory, run the following:
1. `python3 -m venv venv`
2. `source venv/bin/activate`
3. (venv) `pip install -r requirements.txt`

#### Setting up database:
1. (venv) `psql`
2. =# `CREATE DATABASE warbler;`
3. Exit psql
4. (venv) `python seed.py`

#### Start Server
1. `flask run`
2. If mac -> `flask run -p 5001`

## Contributors

- [John Almodovar](https://github.com/johnalmodovar)
- [Gabe Yoro](https://github.com/gabeyoro)
