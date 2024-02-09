FROM python:3.11

# update this if your project is in a directory with a different name!
COPY myproject/_site/ _site/
ENTRYPOINT ["python", "-m", "http.server", "80", "--bind", "0.0.0.0", "--directory", "_site"]