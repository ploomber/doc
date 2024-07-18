FROM rocker/shiny

WORKDIR /app

RUN apt-get update 
RUN apt-get install -y libpq-dev

COPY install.R /app/

RUN Rscript install.R

COPY . /app

ENTRYPOINT ["Rscript", "startApp.R"]