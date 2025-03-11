# copilot-usage-service

The `copilot-usage-service` is a Python FastAPI API with a single endpoint `/usage` to support the Orbital copilot an calculate user copilot credit usage. 

## Development Setup

Ensure that python >=3.13 is installed.  This can be done using pyenv on MacOS

```
brew update
brew install pyenv
pyenv               # Tests install
pyenv install 3     # Installs latest >3
pyenv global 3.13.2 # Set global version
python3 --version   # Test Python version
```

Install `poetry` with the following command

```
curl -sSL https://install.python-poetry.org | python3 -
poetry --version # Test the install
```

Install dependecies

```
poetry install
```

### Docker 
There is a `docker-compose.yaml` file to aid development.  Start the service with

```
docker compose up .
```

Note: there are 2 Dockerfiles
- ./container/development/Dockerfile
- ./container/production/Dockerfile

This is to allow for changes to the dockerfile during development and optimizations in production.  