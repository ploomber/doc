# Dash App Connected to PostgreSQL Database

Interactive Dash Application, connected to PostgreSQL database.

![](app.png)

## Set up local testing environment
To use the app, store the below information locally into your `.env` for `upload.py`. These variables can be found on the `Parameters only` section under `connection details` from your [Neon](https://console.neon.tech/) PostgreSQL dashboard.
```
PGHOST='YOUR_HOST'
PGDATABASE='test'
PGUSER='test_owner'
PGPASSWORD='your_password'
```

Run `python -m pip install -r requirements.txt` to install all necessary packages.

## Upload dataset to your Postgres server
You can download the dataset I'm using [here](https://archive.ics.uci.edu/dataset/320/student+performance) and store them in the `data` folder. Next, `cd data` and run `python csv_mod.py` to obtain `student-mat-min.csv` and `student-por-min.csv`, the extracted dataset that we will be uploading. Run `python upload.py` locally to upload the dataset to your PostgreSQL.

## Local testing
Add the below lines to your `app.py`
```python
from dotenv import load_dotenv

# Load environment variables
load_dotenv(".env")
```

You should remove them once you are done with local testing to avoid error.

Run `gunicorn app:server run --bind 0.0.0.0:80`. You should be able to access the app at `0.0.0.0:80`.

## Upload to Ploomber Cloud
Compress and upload the below files for deployment. Make sure to specify the above environment variables in your [secrets](https://docs.cloud.ploomber.io/en/latest/user-guide/secrets.html). For more details, please refer to our [Dash deployment guide](https://docs.cloud.ploomber.io/en/latest/apps/dash.html)
- app.py
- assets/style.css
- requirements.txt
