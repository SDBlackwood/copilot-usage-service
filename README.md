# copilot-usage-service

The `copilot-usage-service` is a Python FastAPI API with a single endpoint `/usage` to support the Orbital copilot an calculate user copilot credit usage. 

## Docker Set Up
There is a `docker-compose.yaml` file to aid development.  Start the service with

```
docker compose up .
```

Note: there are 2 Dockerfiles
- `./container/development/Dockerfile`
- `./container/production/Dockerfile`

This is to allow for changes to the dockerfile during development and optimizations in production. 

You can then access the usage endpoint on 

```
`http://localhost:8080/usage`
```

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

# Constraints

## Validating the exact cost of the test results
Due to the complexity of the algorithm, it was difficult to assert that my implementation was correct given the time constraints. To actually verify everything I made tests for each part of the algorithm. I wouldn't normally do this as I don't want to make tests for each low-level function. I would rather make tests from the highest point (calling the function) and asserting the total cost, but this would mean manually calculating lots of costs, which I didn't have time for.

## Logging & Tracing
We would want to add logging throughout to allow us to help expose some of the internal workings of the application while it was running. This would be set to DEBUG or INFO in dev and WARNING in prod. We may also want to expose some tracing to allow us to understand the steps of the application and its integration to the other services. Then if there are problems, we can more easily debug issues.
For example, we also fall back to the cost calculation if the report data is invalid. This could indicate a surreptitious issue with that service. By falling back to the cost calculation we are obscuring that issue. We would want to log an error and surface an alert to ensure that the issue is investigated.
