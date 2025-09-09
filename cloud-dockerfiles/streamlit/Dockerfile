FROM python:3.12-slim-bookworm

WORKDIR /srv

# Install base requirements first
RUN pip install streamlit --no-cache-dir

COPY requirements.txt /srv/


# Install Python dependencies
RUN pip install -r requirements.txt --no-cache-dir


# CMD to run the Streamlit app
CMD ["streamlit", "run", "/srv/app.py", \
    "--server.port=80", \
    "--server.headless=true", \
    "--server.address=0.0.0.0", \
    "--browser.gatherUsageStats=false", \
    "--server.enableStaticServing=true", \
    "--server.fileWatcherType=none", \
    "--client.toolbarMode=viewer"]