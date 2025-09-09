FROM python:3.12-slim-bookworm

# Install necessary dependencies for Voila
RUN pip install voila ipywidgets ipykernel --no-cache-dir

WORKDIR /srv

# Copy the requirements.txt to install Python dependencies
COPY requirements.txt /srv/
RUN pip install -r requirements.txt --no-cache-dir

# Copy the application and other necessary files
COPY . /srv/

# CMD to run the Voila app
CMD ["voila", "--port=80", "--no-browser", "app.ipynb", "--Voila.ip='0.0.0.0'"]
