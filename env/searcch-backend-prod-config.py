TESTING = False
DEBUG = False
SQLALCHEMY_ECHO = True
SQLALCHEMY_TRACK_MODIFICATIONS = True
#SESSION_TIMEOUT_IN_MINUTES = 60
SESSION_TIMEOUT_IN_MINUTES = 24*60
SQLALCHEMY_DATABASE_URI = "postgresql+psycopg2cffi://psql_user:psql_password@searcch-backend-prod-postgres:5432/searcchhub"
SHARED_SECRET_KEY = 'shared_secret_key'
DB_AUTO_MIGRATE = True
