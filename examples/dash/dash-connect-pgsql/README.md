# Dash App Connected to PostgreSQL Database

Interactive Dash Application, connected to PostgreSQL database.

![](app.png)

To use the app, store the below information locally into your `.env` for `upload.py`. These variables can be found on the `Parameters only` section under `connection details` from your PostgreSQL dashboard.
```
PGHOST='YOUR_HOST'
PGDATABASE='test'
PGUSER='test_owner'
PGPASSWORD='your_password'
```

run `python3 upload.py` locally to upload the datasets to your PostgreSQL, then compress and upload the below files for deployment. Make sure to specify the above environment variables in your [secrets](https://docs.cloud.ploomber.io/en/latest/user-guide/secrets.html) 
- app.py
- assets/style.css
- Dockerfile
- requirements.txt
