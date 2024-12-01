from flask import Flask
from src.models import db
from config import config
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os
from dotenv import load_dotenv
import logging
from urllib.parse import urlparse

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=getattr(logging, os.getenv('LOG_LEVEL', 'INFO')),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.getenv('LOG_FILE', 'logs/miicoin.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def parse_database_url(url):
    """Parse DATABASE_URL into connection parameters"""
    parsed = urlparse(url)
    return {
        'host': parsed.hostname,
        'user': parsed.username,
        'password': parsed.password,
        'port': parsed.port
    }

def create_database():
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        raise ValueError("DATABASE_URL not found in environment variables")
    
    conn_params = parse_database_url(db_url)
    
    # Connect to PostgreSQL
    try:
        conn = psycopg2.connect(**conn_params)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Create database
        try:
            cursor.execute("CREATE DATABASE miicoin_db")
            logger.info("Database created successfully!")
        except psycopg2.errors.DuplicateDatabase:
            logger.info("Database already exists.")
        except Exception as e:
            logger.error(f"Error creating database: {str(e)}")
            raise
    except Exception as e:
        logger.error(f"Connection error: {str(e)}")
        raise
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

def init_tables():
    try:
        # Create Flask application
        app = Flask(__name__)
        app.config.from_object(config['development'])
        
        # Initialize SQLAlchemy
        db.init_app(app)
        
        # Create tables
        with app.app_context():
            db.create_all()
            logger.info("Tables created successfully!")
    except Exception as e:
        logger.error(f"Error initializing tables: {str(e)}")
        raise

if __name__ == "__main__":
    try:
        create_database()
        init_tables()
        logger.info("Database initialization completed successfully!")
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
