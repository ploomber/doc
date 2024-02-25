FROM osgeo/gdal:ubuntu-small-3.6.3

RUN curl -sS https://bootstrap.pypa.io/get-pip.py | python3
RUN python3 -m pip install --upgrade pip
RUN apt update
RUN apt install python3-dev -y
RUN apt install gcc g++ -y

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
ENTRYPOINT voila --port=80 --no-browser app.ipynb --Voila.ip='0.0.0.0'
