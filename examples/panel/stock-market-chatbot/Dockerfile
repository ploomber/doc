FROM python:3.11

COPY app.py app.py
COPY chat.py chat.py
COPY nasdaq_symbols.csv nasdaq_symbols.csv
COPY stock.py stock.py
COPY image.png image.png
COPY .env .env
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

CMD ["panel", "serve", "app.py", "--port=80", "--address=0.0.0.0", "--allow-websocket-origin=*"]