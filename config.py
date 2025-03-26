class Config:
    UPLOAD_FOLDER = "uploads"
    TALLY_URL = "http://host.docker.internal:9000"
    SQLALCHEMY_DATABASE_URI = "postgresql://user:password@postgres:5432/tallyDB"
    # local configration
    # TALLY_URL = "http://localhost:9000"
    # SQLALCHEMY_DATABASE_URI = "postgresql://postgres:root@localhost:5432/dbname"

