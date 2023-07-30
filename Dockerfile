# Use an official Python runtime as a parent image
FROM public.ecr.aws/lambda/python:3.10

# COPY pyproject.toml poetry.lock .
COPY app ${LAMBDA_TASK_ROOT}/app
COPY main.py ${LAMBDA_TASK_ROOT}/main.py
COPY requirements.txt ${LAMBDA_TASK_ROOT}/requirements.txt

# # Install poetry
# RUN pip install poetry

# # Install dependencies using poetry
# RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi
# # ENV PATH="${PATH}:/root/.local/bin"
RUN pip install -r ${LAMBDA_TASK_ROOT}/requirements.txt

# Set the CMD to your handler (could also be done as a parameter override outside of the Dockerfile)
CMD [ "main.handler" ]
