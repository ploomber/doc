FROM python:3.11

COPY app.py app.py

RUN pip install streamlit

ENTRYPOINT ["streamlit", "run", "app.py", \
            "--server.port=80", \
            "--server.headless=true", \
            "--server.address=0.0.0.0", \
            "--browser.gatherUsageStats=false", \
            "--server.enableStaticServing=true", \
            "--server.baseUrlPath=__PROJECT_ID__", \
            "--server.fileWatcherType=none", \
            "--client.toolbarMode=viewer"]
