# Using AWS Lambda Python base image
FROM public.ecr.aws/lambda/python:3.12

# Set the working directory to the Lambda task root
COPY requirements.txt ${LAMBDA_TASK_ROOT}

# Install necessary packages
RUN pip install -r requirements.txt

# Copy the Lambda function code to the container
COPY ./app ${LAMBDA_TASK_ROOT}/app

# Set the handler to the Lambda function
CMD ["app.main.handler"]
