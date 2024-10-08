FROM rocker/shiny

WORKDIR /app

# install sf dependencies
RUN apt-get -y update && apt-get install -y  libudunits2-dev libgdal-dev libgeos-dev libproj-dev && rm -rf /var/lib/apt/lists/*

COPY install.R /app/

RUN Rscript install.R

COPY . /app

ENTRYPOINT ["Rscript", "startApp.R"]