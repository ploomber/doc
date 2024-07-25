# Streamlit App Connected to Postgres
To showcase the power of using a database with Streamlit apps to display live data, this app enables users to insert their own data into a table on their database. The new data is then automatically displayed and used in the app. 

![](app.png)

## Run App
To run this app locally ensure you set the `DB_URI` variable in `app.py` to your personal database URI and that you have installed all the packages listed in requirements.txt.

## Deployment
When deploying this app on Ploomber Cloud you need to set the `DB_URI` as a secret. Refer to the [documentation](https://docs.cloud.ploomber.io/en/latest/user-guide/secrets.html) to learn more.