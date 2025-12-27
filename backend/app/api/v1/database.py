from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from app.services.db_connector import connect_to_database, DatabaseConnector, DatabaseType
from app.services.data_analyzer import EnterpriseDataAnalyzer
from app.api.v1.quality import store_report
import uuid

router = APIRouter()


class DatabaseConnectionRequest(BaseModel):
    """Request model for database connection"""
    db_type: str  # postgresql, mysql, mongodb, sqlite
    host: str = "localhost"
    port: Optional[int] = None
    database: str
    username: Optional[str] = None
    password: Optional[str] = None
    ssl: Optional[bool] = False


class TableAnalysisRequest(BaseModel):
    """Request model for table analysis"""
    db_type: str
    host: str = "localhost"
    port: Optional[int] = None
    database: str
    username: Optional[str] = None
    password: Optional[str] = None
    table_name: str
    row_limit: Optional[int] = 10000


@router.post("/test")
async def test_database_connection(request: DatabaseConnectionRequest):
    """Test connection to a client database"""
    
    config = {
        "host": request.host,
        "port": request.port,
        "database": request.database,
        "username": request.username,
        "password": request.password,
        "ssl": request.ssl
    }
    
    result = connect_to_database(request.db_type, config)
    
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Connection failed"))
    
    return {
        "status": "success",
        "connection": result,
        "message": f"Successfully connected to {request.db_type} database"
    }


@router.post("/list-tables")
async def list_database_tables(request: DatabaseConnectionRequest):
    """List all tables/collections in a database"""
    
    config = {
        "host": request.host,
        "port": request.port,
        "database": request.database,
        "username": request.username,
        "password": request.password
    }
    
    try:
        db_type_enum = DatabaseType(request.db_type.lower())
        connector = DatabaseConnector(db_type_enum, config)
        
        # Test connection first
        test_result = connector.test_connection()
        if not test_result.get("success"):
            raise HTTPException(status_code=400, detail=test_result.get("error"))
        
        # List tables
        tables = connector.list_tables()
        
        return {
            "status": "success",
            "database": request.database,
            "tables": tables,
            "count": len(tables)
        }
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Unsupported database type: {request.db_type}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze-table")
async def analyze_database_table(request: TableAnalysisRequest):
    """Analyze a specific table from a client database"""
    
    config = {
        "host": request.host,
        "port": request.port,
        "database": request.database,
        "username": request.username,
        "password": request.password
    }
    
    try:
        db_type_enum = DatabaseType(request.db_type.lower())
        connector = DatabaseConnector(db_type_enum, config)
        
        # Test connection first
        test_result = connector.test_connection()
        if not test_result.get("success"):
            raise HTTPException(status_code=400, detail=test_result.get("error"))
        
        # Fetch data
        df = connector.fetch_table_data(request.table_name, request.row_limit)
        
        # Generate source ID
        source_id = str(uuid.uuid4())
        
        # Analyze data
        analyzer = EnterpriseDataAnalyzer(df, f"{request.database}.{request.table_name}")
        report = analyzer.generate_full_report()
        
        # Add source info
        report["source_type"] = "database"
        report["database_type"] = request.db_type
        report["database_name"] = request.database
        report["table_name"] = request.table_name
        
        # Store report
        store_report(source_id, report)
        
        return {
            "status": "success",
            "source_id": source_id,
            "table_name": request.table_name,
            "rows_analyzed": len(df),
            "quality_score": report.get("quality_score", {}).get("overall_score"),
            "grade": report.get("quality_score", {}).get("grade"),
            "message": f"Successfully analyzed table {request.table_name}"
        }
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Unsupported database type: {request.db_type}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/table-schema")
async def get_table_schema(request: TableAnalysisRequest):
    """Get schema information for a table"""
    
    config = {
        "host": request.host,
        "port": request.port,
        "database": request.database,
        "username": request.username,
        "password": request.password
    }
    
    try:
        db_type_enum = DatabaseType(request.db_type.lower())
        connector = DatabaseConnector(db_type_enum, config)
        
        schema = connector.get_table_schema(request.table_name)
        
        return {
            "status": "success",
            "schema": schema
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/supported-types")
async def get_supported_database_types():
    """Get list of supported database types"""
    return {
        "status": "success",
        "supported_types": [
            {
                "id": "postgresql",
                "name": "PostgreSQL",
                "default_port": 5432,
                "description": "Open-source relational database"
            },
            {
                "id": "mysql",
                "name": "MySQL",
                "default_port": 3306,
                "description": "Popular open-source relational database"
            },
            {
                "id": "mongodb",
                "name": "MongoDB",
                "default_port": 27017,
                "description": "NoSQL document database"
            },
            {
                "id": "sqlite",
                "name": "SQLite",
                "default_port": None,
                "description": "Embedded file-based database"
            }
        ]
    }
