# Flask Boilerplate

### Technical Details
- **Python Version**: 3.10
- **Flask Version**: 3.0.3

### Setup Instructions

1. **Create and Activate a Virtual Environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
2. Install all dependencies by using `pip install -r requirements.txt`.

### Setup Config File

- Run `cp /home/flask_boilerplate/config/config_sample.yml /home/flask_boilerplate/config/config.yml`.
- Now update the newly created `config.yml` file.

### Create the database

```
# Login to postgres session
sudo -u postgres psql

# Create a database with below command.
CREATE DATABASE 'flask-boilerplate';

# Press \q to exit the postgres session
\q
```

- run migrations using `flask db upgrade`

### Alembic - Generating Migrations

- Once models are changed for any component, run following commands to create its migrations file & reflect it into the database

```
flask db migrate -m "Write description of migration here" --rev-id=<REVISION_ID>
```

- Run `flask db upgrade` to reflect changes in th database.

### Important alembic commands for reference

- To rollback 1 migration: `flask db downgrade`
- Downgrade to specific migration: `flask db downgarde <revision>`

### Run Project

- Run the flask project by using `python main.py`.
