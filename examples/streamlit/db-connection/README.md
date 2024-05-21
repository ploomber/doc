# DB Connection 

This is a sample app for demonstrating DB connections in Streamlit. To run this app ensure you set the `DB_URI` environment variable:

```sh 
export DB_URI=sqlite:///numbers.db
```

Note that while this example uses `SQLite` for simplicity, you can substitute the URI with the [SQLAlchemy URI](https://docs.sqlalchemy.org/en/20/core/engines.html#database-urls) corresponding to your specific database. Here's the format:

```python
dialect+driver://username:password@host:port/database
```

## Deployment

When deploying this app on Ploomber Cloud you need to set the `DB_URI` as a secret. Refer to the [documentation](https://docs.cloud.ploomber.io/en/latest/user-guide/secrets.html) to learn more.