class Config:
    UPLOAD_FOLDER = "uploads"
    TALLY_URL = "http://localhost:9000"
    SQLALCHEMY_DATABASE_URI = "mssql+pyodbc:///?odbc_connect=DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=TallyPrime;Trusted_Connection=yes;"
    SQLALCHEMY_TRACK_MODIFICATIONS = False