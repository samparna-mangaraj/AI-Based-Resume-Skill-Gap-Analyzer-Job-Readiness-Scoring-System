import os
import sys
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Add the app directory to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), "app"))

load_dotenv()

def test_connection():
    DB_USER = os.getenv("DB_USER")
    DB_PASS = os.getenv("DB_PASSWORD")
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")
    DB_NAME = os.getenv("DB_NAME")

    print(f"--- DATABASE CONNECTION TEST ---")
    print(f"Connecting to: {DB_HOST}:{DB_PORT} as {DB_USER}")
    
    url = f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    
    try:
        engine = create_engine(url)
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            print("Successfully connected to the database!")
            
            # Check if tables exist
            result = connection.execute(text("SHOW TABLES"))
            tables = [row[0] for row in result]
            print(f"Tables found: {', '.join(tables) if tables else 'None'}")
            
    except Exception as e:
        print(f"CONNECTION FAILED!")
        print(f"Error: {str(e)}")
        print("\nPossible solutions:")
        print("1. Ensure MySQL server is running.")
        print("2. Verify credentials in backend/.env")
        print("3. Ensure the database 'skillgap_db' exists.")

if __name__ == "__main__":
    test_connection()
