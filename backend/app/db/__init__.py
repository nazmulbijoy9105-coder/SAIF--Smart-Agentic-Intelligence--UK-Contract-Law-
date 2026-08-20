import os
from databases import Database

# Render provides the DATABASE_URL environment variable automatically
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/saif_db")

# Instantiate the database connection pool
database = Database(DATABASE_URL)
