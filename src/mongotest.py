import os
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

def test_mongodb_connection():
    try:
        # Retrieve the connection string from the environment variable
        mongo_db_connection_string = os.getenv("MONGO_DB_CONNECTION_STRING")
        
        if not mongo_db_connection_string:
            raise ValueError("MONGO_DB_CONNECTION_STRING is not set in the environment variables")

        client = MongoClient(mongo_db_connection_string)
        # The ismaster command is cheap and does not require auth.
        client.admin.command('ismaster')
        print("MongoDB connection successful")
    except ServerSelectionTimeoutError as e:
        print(f"MongoDB connection failed: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    test_mongodb_connection()
