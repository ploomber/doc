FROM r-base
COPY . .
RUN Rscript install.R
ENTRYPOINT ["Rscript", "startApp.R"]
