FROM python:3.11

# assume your dashboard is named dashboard.xprjson
COPY dashboard.xprjson dashboard.xprjson

# install py-chalk-it and gunicorn
RUN pip install py-chalk-it gunicorn --no-cache-dir

# this configuration is needed for your app to work, do not change it
ENTRYPOINT ["gunicorn", "chlkt.render:app", "run", "--bind", "0.0.0.0:80"]
