FROM rocker/shiny:4.3.3

WORKDIR /srv

COPY install.R /srv/
RUN Rscript install.R

COPY . /srv

ENTRYPOINT ["Rscript", "startApp.R"]
