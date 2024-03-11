FROM rocker/shiny


WORKDIR /app

RUN apt update && apt install -y libglpk-dev

COPY install.R /app/

RUN Rscript install.R

COPY . /app

ENTRYPOINT ["Rscript", "startApp.R"]