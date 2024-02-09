FROM python:3.11

RUN curl -LO https://quarto.org/download/latest/quarto-linux-amd64.deb
RUN apt-get update
RUN apt-get install gdebi-core -y
RUN gdebi quarto-linux-amd64.deb --non-interactive

# update this if your project is in a directory with a different name!
COPY myproject/ myproject/
RUN quarto render myproject

ENTRYPOINT ["python", "-m", "http.server", "80", "--bind", "0.0.0.0", "--directory", "myproject/_site"]