[![Python 3.10](https://img.shields.io/badge/python-3.10-blue.svg)](https://www.python.org/downloads/release/python-3100/)
![example workflow](https://github.com/inna-tuzhikova/script_license_manager/actions/workflows/lint_test.yml/badge.svg)
# Script License Manager
**Final Project (OTUS. Python Developer. Professional)**

## Description
App for serving python scripts download requests. Scripts are collected from 
repository and outputted as encoded text files.

Backend:
* Scripts API build with Django rest framework
* Postgres
* Redis (TODO)

Frontend:
* Client web application (TODO)

## Run dev
`docker-compose -f docker-compose.dev.yml up --build`

## Run linters and tests
`docker-compose -f docker-compose.ci.yml up --build`

## Docs
Browsable API `/api/v1/`

Swagger `/api/v1/swagger/`
