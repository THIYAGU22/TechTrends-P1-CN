#Step 1 : Run the container on base image
FROM python:2.7-alpine
LABEL maintainer="Thiyagarajan"

# Step 2: Expose the port to serve the request
EXPOSE 3111

# Step 3 : Setup working directory and add the necessary files
WORKDIR /app
COPY . /app

# Step 4:  Install pip requirements
COPY ./requirements.txt /app/requirements.txt
RUN python -m pip install -r requirements.txt

# Step 5 : Initialize the schema and insert dummy datas
RUN python init_db.py

#Step 6: Run the command on container once its starts
CMD [ "python" , "app.py" ]