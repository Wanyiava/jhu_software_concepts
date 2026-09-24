import os
os.environ["DATABASE_URL"] = "postgresql://postgres:password@127.0.0.1:5432/test_db"
os.environ["PGPASSWORD"] = "password"
os.environ["PGUSER"] = "postgres"
os.environ["PGHOST"] = "127.0.0.1"