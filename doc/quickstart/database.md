# Deploy a Database

## 1. Click on "Database" -> "New"
![](../static/db-new.png)

## 2. Fill out the form
Here you'll need to choose a database name, a username, and password. You also have the option to change the default hardware on which your database will be running.
![](../static/db-enter-info.png)

```{important}
Generate a strong password, preferably with a mix of uppercase and lowercase letters, numbers, and special characters. Store this password securely as you'll need it to connect to your database.
```

## 3. Wait for the deployment to finish
Once created, the database will be deployed, this can take up to a minute. When your database is running, you are ready to connect to it.
![](../static/db-running.png)

## 4. Connecting to your Database
Once your database is deployed, you can connect to it directly from the CLI, or through tools like [pgAdmin](https://www.pgadmin.org/).

### Connecting to your Database from the CLI
To connect to the database from the terminal, you'll first need psql, which can be installed with:

```sh
# For Debian/Ubuntu
sudo apt-get install postgresql-client

# For macOS using Homebrew
brew install libpq
brew link --force libpq

# For Windows
# Download the installer from https://www.postgresql.org/download/windows/
```

Once installed, copy the PSQL command from the UI into your terminal to directly connect to your database. This will prompt you for the password. This one can be found above the PSQL command.

![](../static/db-psql.png)

```sh
$ psql -h {DATABASE-URL} -U {USERNAME} {DATABASE_NAME}
Password for user ...: {DATABASE_PASSWORD}
```

Congratulations, you are now connected to your database!

You can run the following commands to create a new table:

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Insert a test user
INSERT INTO users (username, email) VALUES ('testuser', 'test@example.com');

-- Verify the insertion
SELECT * FROM users;
```

### Connecting to your Database from pgAdmin

1. Open pgAdmin on your computer
2. Right-click on "Servers" in the browser panel and select "Create" > "Server..."
3. In the "General" tab, enter a name for your server connection
4. Switch to the "Connection" tab and enter the following details:
   - Host name/address: Your database URL (from the UI)
   - Port: 5432 (default PostgreSQL port)
   - Maintenance database: Your database name
   - Username: Your database username
   - Password: Your database password
5. Click "Save" to connect to your database
6. Your database will appear in the server list, and you can expand it to see tables and other objects

