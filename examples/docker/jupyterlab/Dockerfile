FROM python:3.11

RUN pip install jupyterlab --no-cache-dir

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt --no-cache-dir

COPY jupyter_server_config.py /root/.jupyter/jupyter_server_config.py

ENTRYPOINT ["jupyter", "lab", "--ip=0.0.0.0", "--no-browser",  "--port=80", "-y", "--allow-root"]