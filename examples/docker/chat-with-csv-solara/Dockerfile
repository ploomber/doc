FROM python:3.11

COPY app.py app.py
COPY chat.py chat.py
COPY static/ static/
RUN pip install git+https://github.com/ploomber/jupysql.git@master
RUN pip install requests solara openai pandas duckdb duckdb-engine matplotlib


ENTRYPOINT ["solara", "run", "app.py", "--host=0.0.0.0", "--port=80"]