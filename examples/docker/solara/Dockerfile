FROM python:3.11

COPY app.py app.py
RUN pip install spacy && python -m spacy download en_core_web_sm
RUN pip install solara pytextrank pandas



ENTRYPOINT ["solara", "run", "app.py", "--host=0.0.0.0", "--port=80"]