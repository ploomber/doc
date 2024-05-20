# DB Connection 

This is a sample app for demonstrating DB connections in Streamlit. To run this app ensure you set the environment variable:

```sh 
export DB_URI=sqlite:///numbers.db
```

Note that this URI is a [SQLAlchemy URI](https://docs.sqlalchemy.org/en/20/core/engines.html#database-urls). It can be replaced with the URI of your specific DB.

## Deployment

When deploying this app on Ploomber Cloud you need to set the `DB_URI` as a secret. Refer to the [documentation](https://docs.cloud.ploomber.io/en/latest/user-guide/secrets.html) to learn more.