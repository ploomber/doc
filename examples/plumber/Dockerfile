FROM rstudio/plumber

WORKDIR /app

COPY . /app

RUN R -e "install.packages('caret', repos='http://cran.rstudio.com/')"

EXPOSE 80

ENTRYPOINT ["Rscript", "main.R"]