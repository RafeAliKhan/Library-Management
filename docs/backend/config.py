import os

SECRET_KEY = os.environ.get("SECRET_KEY", "change-me-in-production")
DATABASE = os.environ.get("DATABASE", os.path.join(os.path.dirname(__file__), "library.db"))
LOAN_DAYS = 14
FINE_PER_DAY = 0.50
