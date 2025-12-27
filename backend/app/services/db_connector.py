"""
Database Connection Service
Handles connections to client databases (PostgreSQL, MySQL, MongoDB)
"""
import pandas as pd
from typing import Dict, Any, Optional, List
from enum import Enum


class DatabaseType(str, Enum):
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    MONGODB = "mongodb"
    SQLITE = "sqlite"


class DatabaseConnector:
    """
    Universal database connector for analyzing client data.
    Supports PostgreSQL, MySQL, MongoDB, and SQLite.
    """
    
    def __init__(self, db_type: DatabaseType, config: Dict[str, Any]):
        self.db_type = db_type
        self.config = config
        self.connection = None
        
    def get_connection_string(self) -> str:
        """Generate connection string based on database type"""
        host = self.config.get("host", "localhost")
        port = self.config.get("port")
        database = self.config.get("database", "")
        username = self.config.get("username", "")
        password = self.config.get("password", "")
        
        if self.db_type == DatabaseType.POSTGRESQL:
            port = port or 5432
            return f"postgresql://{username}:{password}@{host}:{port}/{database}"
        
        elif self.db_type == DatabaseType.MYSQL:
            port = port or 3306
            return f"mysql+pymysql://{username}:{password}@{host}:{port}/{database}"
        
        elif self.db_type == DatabaseType.SQLITE:
            return f"sqlite:///{self.config.get('file_path', ':memory:')}"
        
        elif self.db_type == DatabaseType.MONGODB:
            port = port or 27017
            return f"mongodb://{username}:{password}@{host}:{port}/{database}"
        
        return ""
    
    def test_connection(self) -> Dict[str, Any]:
        """Test database connection"""
        try:
            if self.db_type == DatabaseType.MONGODB:
                return self._test_mongodb_connection()
            else:
                return self._test_sql_connection()
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to connect to database"
            }
    
    def _test_sql_connection(self) -> Dict[str, Any]:
        """Test SQL database connection"""
        try:
            from sqlalchemy import create_engine, text
            
            conn_string = self.get_connection_string()
            engine = create_engine(conn_string)
            
            with engine.connect() as conn:
                # Test query
                if self.db_type == DatabaseType.POSTGRESQL:
                    result = conn.execute(text("SELECT version()"))
                    version = result.fetchone()[0]
                elif self.db_type == DatabaseType.MYSQL:
                    result = conn.execute(text("SELECT VERSION()"))
                    version = result.fetchone()[0]
                else:
                    result = conn.execute(text("SELECT sqlite_version()"))
                    version = result.fetchone()[0]
            
            return {
                "success": True,
                "message": "Connection successful",
                "database_type": self.db_type.value,
                "version": version
            }
        except ImportError:
            return {
                "success": False,
                "error": "Required database driver not installed",
                "message": "Please install: pip install sqlalchemy psycopg2-binary pymysql"
            }
    
    def _test_mongodb_connection(self) -> Dict[str, Any]:
        """Test MongoDB connection"""
        try:
            from pymongo import MongoClient
            
            host = self.config.get("host", "localhost")
            port = self.config.get("port", 27017)
            username = self.config.get("username")
            password = self.config.get("password")
            database = self.config.get("database", "test")
            
            if username and password:
                client = MongoClient(f"mongodb://{username}:{password}@{host}:{port}/")
            else:
                client = MongoClient(host, port)
            
            # Test connection
            db = client[database]
            collections = db.list_collection_names()
            
            return {
                "success": True,
                "message": "Connection successful",
                "database_type": "mongodb",
                "collections_count": len(collections),
                "collections": collections[:10]  # First 10
            }
        except ImportError:
            return {
                "success": False,
                "error": "pymongo not installed",
                "message": "Please install: pip install pymongo"
            }
    
    def list_tables(self) -> List[str]:
        """List all tables/collections in the database"""
        try:
            if self.db_type == DatabaseType.MONGODB:
                return self._list_mongodb_collections()
            else:
                return self._list_sql_tables()
        except Exception as e:
            return []
    
    def _list_sql_tables(self) -> List[str]:
        """List SQL tables"""
        from sqlalchemy import create_engine, inspect
        
        conn_string = self.get_connection_string()
        engine = create_engine(conn_string)
        inspector = inspect(engine)
        
        return inspector.get_table_names()
    
    def _list_mongodb_collections(self) -> List[str]:
        """List MongoDB collections"""
        from pymongo import MongoClient
        
        host = self.config.get("host", "localhost")
        port = self.config.get("port", 27017)
        database = self.config.get("database", "test")
        
        client = MongoClient(host, port)
        db = client[database]
        
        return db.list_collection_names()
    
    def fetch_table_data(self, table_name: str, limit: int = 10000) -> pd.DataFrame:
        """Fetch data from a table/collection"""
        try:
            if self.db_type == DatabaseType.MONGODB:
                return self._fetch_mongodb_data(table_name, limit)
            else:
                return self._fetch_sql_data(table_name, limit)
        except Exception as e:
            raise Exception(f"Failed to fetch data: {str(e)}")
    
    def _fetch_sql_data(self, table_name: str, limit: int) -> pd.DataFrame:
        """Fetch data from SQL table"""
        from sqlalchemy import create_engine
        
        conn_string = self.get_connection_string()
        engine = create_engine(conn_string)
        
        query = f"SELECT * FROM {table_name} LIMIT {limit}"
        return pd.read_sql(query, engine)
    
    def _fetch_mongodb_data(self, collection_name: str, limit: int) -> pd.DataFrame:
        """Fetch data from MongoDB collection"""
        from pymongo import MongoClient
        
        host = self.config.get("host", "localhost")
        port = self.config.get("port", 27017)
        database = self.config.get("database", "test")
        
        client = MongoClient(host, port)
        db = client[database]
        collection = db[collection_name]
        
        cursor = collection.find().limit(limit)
        data = list(cursor)
        
        # Convert ObjectId to string
        for doc in data:
            if '_id' in doc:
                doc['_id'] = str(doc['_id'])
        
        return pd.DataFrame(data)
    
    def get_table_schema(self, table_name: str) -> Dict[str, Any]:
        """Get schema/structure of a table"""
        try:
            if self.db_type == DatabaseType.MONGODB:
                return self._get_mongodb_schema(table_name)
            else:
                return self._get_sql_schema(table_name)
        except Exception as e:
            return {"error": str(e)}
    
    def _get_sql_schema(self, table_name: str) -> Dict[str, Any]:
        """Get SQL table schema"""
        from sqlalchemy import create_engine, inspect
        
        conn_string = self.get_connection_string()
        engine = create_engine(conn_string)
        inspector = inspect(engine)
        
        columns = inspector.get_columns(table_name)
        primary_keys = inspector.get_pk_constraint(table_name)
        
        return {
            "table_name": table_name,
            "columns": [
                {
                    "name": col["name"],
                    "type": str(col["type"]),
                    "nullable": col.get("nullable", True)
                }
                for col in columns
            ],
            "primary_keys": primary_keys.get("constrained_columns", []),
            "row_count": None  # Would require another query
        }
    
    def _get_mongodb_schema(self, collection_name: str) -> Dict[str, Any]:
        """Infer MongoDB collection schema from sample documents"""
        from pymongo import MongoClient
        
        host = self.config.get("host", "localhost")
        port = self.config.get("port", 27017)
        database = self.config.get("database", "test")
        
        client = MongoClient(host, port)
        db = client[database]
        collection = db[collection_name]
        
        # Sample documents to infer schema
        sample = list(collection.find().limit(100))
        
        # Infer fields from sample
        fields = {}
        for doc in sample:
            for key, value in doc.items():
                if key not in fields:
                    fields[key] = type(value).__name__
        
        return {
            "collection_name": collection_name,
            "fields": fields,
            "sample_count": len(sample),
            "estimated_count": collection.estimated_document_count()
        }


def connect_to_database(db_type: str, config: Dict[str, Any]) -> Dict[str, Any]:
    """Helper function to connect and test database"""
    try:
        db_type_enum = DatabaseType(db_type.lower())
        connector = DatabaseConnector(db_type_enum, config)
        result = connector.test_connection()
        
        if result["success"]:
            result["tables"] = connector.list_tables()
        
        return result
    except ValueError:
        return {
            "success": False,
            "error": f"Unsupported database type: {db_type}",
            "supported_types": [t.value for t in DatabaseType]
        }
