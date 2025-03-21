# Deploy a Database


## 1. Click on "Database" -> "New"

![](../static/db-new.png)

## 2. Fill out the form

Here you'll need to choose a Database name, a username and password. Once done, you have the option to change the default hardware on which your database will be running.

![](../static/db-enter-info.png)

```{important}
Generate a strong password, ...
```

## 3. Wait for the deployment to finish

Once created, the database will be deploy, this can take up to a minute. Once your database is running, you are ready to connect to it

![](../static/db-running.png)

## 4. Connecting to your Database

Once your database deploy, you can connect to it directly from the CLI, or for [PgAdmin](https://www.pgadmin.org/)

### Connecting to you Database from the CLI

To connect to the database from the terminal, you'll first need psql, which can be installed with:
```sh

```

Once installed, copy the PSQL command from the UI into your terminal to direclty connect to your database. This one will be in the following format, representing the URL, database username & password


```sh
psql -h {DATABASE-URL} -U {USERNAME} {DATABASE_NAME}
```

![](../static/db-psql.png)

Congratualtion, you are now connected to your database, run the following commands to create a new tables:
```sql


```

### Connecting to you Database from the PgAdmin


## Connecting you Python app to your Database


## Connecting with JupySQL



