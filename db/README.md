# Database Documentation

This README provides an overview of the database schema design, the usage of Alembic for database migrations, and how migrations are managed.

## Database Schema Design

The database schema is designed using SQLAlchemy ORM. The schema is defined in the `db` directory.
The schema is designed to store the following information:

- **Feed**: Stores information about individual feeds, including URL, category, publisher ID, and creation/modification timestamps.
- **Article**: Contains details about articles fetched from feeds, such as title, publish time, content type, and associated feed ID.
- **Publisher**: Stores information about publishers, including name, site URL, favicon URL, and cover URL.
- **Channel**: Contains details about channels/categories associated with feeds and articles.
- **Locale**: Stores locale information, such as locale code and description.
- **FeedUpdateRecord**: Records the last build time and build timedelta for each feed, along with the frequency of updates per day.

## Directory Structure

The database schema is defined in the following files:

```
db/
├── alembic/
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│       ├── 001_initial.py
│       └── 002_add_feed_update_record_table.py
│   ├── tables/
│   │   ├── __init__.py
│   │   ├── article.py
│   │   ├── feed.py
│   │   ├── publisher.py
│   │   ├── channel.py
│   │   ├── locale.py
│   │   └── feed_update_record.py
│
└──

```

## Usage of Alembic

Alembic is used for database migrations. It provides a flexible way to
manage changes to the database schema over time while keeping track of version history. Here's how Alembic is used:

**Initializing Alembic:** The project includes an Alembic environment configured with a migrations directory to store migration scripts.

**Generating Migrations:** New migrations are generated automatically using the alembic revision command whenever changes are made to the database schema.

**Applying Migrations:** Migration scripts are applied to the database using the alembic upgrade command to bring the database schema up to date with the latest changes.

**Rolling Back Migrations:** If needed, migrations can be rolled back using the alembic downgrade command.


## Managing Migrations

Migrations are managed using the following steps:

- **Creation of Migration Scripts:** Whenever there's a change to the database schema, a new migration script is generated using Alembic.
- **Review and Testing:** Before applying migrations to the production database, they should be reviewed and tested in a development or staging environment.
- **Applying Migrations:** Once tested successfully, migrations are applied to the production database to implement schema changes.
- **Version Control:** Migration scripts, along with other project files, are stored in version control (e.g., Git) to track changes and ensure collaboration among team members.
- **Documentation:** It's essential to document each migration thoroughly, including the purpose of the change, any dependencies, and potential impacts on the application.

By following these steps, database schema changes can be managed effectively while maintaining data integrity and minimizing downtime.

## Database Migration Commands

- **Generate/Add new Migration:**
```
alembic revision -m "Description of Migration"
```
- **Apply Migrations:**
```
alembic upgrade head
```
- **Rollback Migrations:**
```
alembic upgrade head
```
- **View Migration History:**
```
alembic history
```

**Note:** Make sure when add/modify the schema, you need to generate a new migration script and apply it to the database. Update the SQL ORM table in `tables/` accordingly.
