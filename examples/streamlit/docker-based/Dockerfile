FROM continuumio/miniconda3

WORKDIR /srv
COPY . /srv

RUN pip install streamlit --no-cache-dir

ENTRYPOINT ["streamlit", "run", "app.py", \
            "--server.port=80", \
            "--server.headless=true", \
            "--server.address=0.0.0.0", \
            "--browser.gatherUsageStats=false", \
            "--server.enableStaticServing=true", \
            "--server.fileWatcherType=none", \
            # hide the Streamlit menu
            "--client.toolbarMode=viewer"]
