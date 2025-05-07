"""
Database Utilities for APE-Core

This module provides utilities for database operations.
"""

import os
import pymysql
from typing import Dict, List, Any, Optional, Tuple, Union

class DBConnection:
    """Database connection manager"""
    
    def __init__(
        self,
        host: str,
        port: int,
        user: str,
        password: str,
        database: str
    ):
        """
        Initialize database connection
        
        Args:
            host: Database host
            port: Database port
            user: Database user
            password: Database password
            database: Database name
        """
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self._connection = None
    
    def connect(self) -> bool:
        """
        Establish database connection
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            self._connection = pymysql.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database,
                cursorclass=pymysql.cursors.DictCursor
            )
            
            return True
        except Exception:
            self._connection = None
            return False
    
    def get_connection(self):
        """
        Get database connection
        
        Returns:
            Database connection
        """
        if self._connection is None or not self._connection.open:
            self.connect()
        
        return self._connection
    
    def close(self) -> bool:
        """
        Close database connection
        
        Returns:
            True if closed successfully, False otherwise
        """
        try:
            if self._connection and self._connection.open:
                self._connection.close()
            
            self._connection = None
            return True
        except Exception:
            return False
    
    def execute_query(
        self,
        query: str,
        params: Optional[Union[Dict[str, Any], Tuple, List]] = None
    ) -> Dict[str, Any]:
        """
        Execute SQL query
        
        Args:
            query: SQL query
            params: Query parameters
            
        Returns:
            Query results
        """
        try:
            connection = self.get_connection()
            
            if connection is None:
                return {"success": False, "error": "Failed to establish database connection"}
            
            cursor = connection.cursor()
            cursor.execute(query, params or ())
            
            if query.strip().upper().startswith("SELECT"):
                results = cursor.fetchall()
                return {
                    "success": True,
                    "data": {
                        "rows": results,
                        "row_count": len(results),
                        "column_names": [col[0] for col in cursor.description] if cursor.description else []
                    }
                }
            else:
                connection.commit()
                return {
                    "success": True,
                    "data": {
                        "affected_rows": cursor.rowcount,
                        "last_insert_id": cursor.lastrowid
                    }
                }
        except Exception as e:
            return {"success": False, "error": str(e)}

def create_connection_from_env(prefix: str = "APE_DB") -> DBConnection:
    """
    Create database connection from environment variables
    
    Args:
        prefix: Environment variable prefix
        
    Returns:
        Database connection instance
    """
    host = os.environ.get(f"{prefix}_HOST", "localhost")
    port = int(os.environ.get(f"{prefix}_PORT", "3306"))
    user = os.environ.get(f"{prefix}_USER", "root")
    password = os.environ.get(f"{prefix}_PASSWORD", "")
    database = os.environ.get(f"{prefix}_NAME", "")
    
    return DBConnection(host, port, user, password, database)

def sanitize_sql(query: str) -> str:
    """
    Sanitize SQL query for safety
    
    Args:
        query: SQL query
        
    Returns:
        Sanitized query
    """
    # Basic sanitization - remove multiple semicolons and dangerous commands
    sanitized = query.strip()
    
    # Remove dangerous SQL commands for read-only operations
    dangerous_commands = [
        "DROP", "TRUNCATE", "DELETE", "UPDATE", "INSERT", "ALTER", "CREATE"
    ]
    
    if any(sanitized.upper().startswith(cmd) for cmd in dangerous_commands):
        raise ValueError(f"Dangerous SQL command detected: {sanitized}")
    
    return sanitized