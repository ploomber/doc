# dockerfile for deploying shiny-r apps
FROM rocker/shiny

WORKDIR /app

# Caching Introduced here
COPY install.R /app/

RUN Rscript install.R

COPY . /app

ENTRYPOINT ["Rscript", "startApp.R"]
