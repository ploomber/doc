FROM rocker/shiny

WORKDIR /app

RUN apt update && apt install -y libglpk-dev

RUN sudo apt-get install libpq-dev

COPY install.R /app/

RUN Rscript install.R

COPY . /app

ENTRYPOINT ["Rscript", "startApp.R"]