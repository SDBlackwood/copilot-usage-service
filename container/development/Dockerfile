FROM python:3.13.2 as python-base

# Set the working directory in the container
WORKDIR /code

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    # prevents python creating .pyc files
    PYTHONDONTWRITEBYTECODE=1 \
    \
    # pip
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    \
    # poetry
    # https://python-poetry.org/docs/configuration/#using-environment-variables
    POETRY_VERSION=2.1.1 \
    # make poetry install to this location
    POETRY_HOME="/opt/poetry" \
    # make poetry create the virtual environment in the project's root
    # it gets named `.venv`
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    # do not ask any interactive question
    POETRY_NO_INTERACTION=1

# Set an poetry and the venv on the PATH
ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"

################################
# BUILDER
# Build the dependecies
################################
FROM python-base as builder-base

WORKDIR /code

# Install poetry 
RUN curl -sSL https://install.python-poetry.org | python3 -

# Copy the poetry.lock and pyproject.toml files into the container
COPY ./pyproject.toml /code/pyproject.toml
COPY ./poetry.lock /code/poetry.lock

# Install the dependencies without development dependencies
RUN poetry install --without development

################################
# DEVELOPMENT
# Image used during development / testing
################################
FROM python-base as development
ENV FASTAPI_ENV=development

# Set the working directory in the container
WORKDIR /code

# Copy in our built poetry + venv
COPY --from=builder-base $POETRY_HOME $POETRY_HOME

# Copy the poetry.lock and pyproject.toml files into the container
COPY ./pyproject.toml /code/pyproject.toml
COPY ./poetry.lock /code/poetry.lock

# Install the dependencies with development dependencies
RUN poetry install

# Copy the rest of the application code into the container
COPY ./app /code/app

# Expose the port
EXPOSE 8000

# Run the application
CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]