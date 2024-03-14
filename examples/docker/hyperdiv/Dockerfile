FROM python:3.11

# Copy the app code into the image
COPY app.py app.py
# Install Hyperdiv
RUN pip install hyperdiv --no-cache-dir

# Put Hyperdiv in production mode,
# Running on 0.0.0.0:80
ENV HD_PRODUCTION=1
ENV HD_HOST=0.0.0.0
ENV HD_PORT=80

# Start the app
ENTRYPOINT ["python", "app.py"]
