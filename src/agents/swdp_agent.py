"""
SWDP Agent for APE-Core

This module provides integration with SWDP (Software Development Platform) 
services via SQL database access.
"""

import os
import json
import pymysql
from typing import Dict, List, Any, Optional, Tuple, Union
from ..core.agent_interface import DBAgent

class SWDPAgent(DBAgent):
    """Agent for interacting with SWDP via SQL"""
    
    def __init__(self):
        """Initialize the SWDP agent"""
        self.host = os.environ.get("APE_SWDP_DB_HOST", "internal-swdp-db.com")
        self.port = int(os.environ.get("APE_SWDP_DB_PORT", "3306"))
        self.user = os.environ.get("APE_SWDP_DB_USER", "swdp-user")
        self.password = os.environ.get("APE_SWDP_DB_PASSWORD", "dummy-password")
        self.database = os.environ.get("APE_SWDP_DB_NAME", "swdp")
        
        # 프로젝트 루트 디렉토리를 기준으로 스키마 파일 경로 설정
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        default_schema_path = os.path.join(base_dir, "schemas", "swdp-db.json")
        self.schema_path = os.environ.get("APE_SWDP_SCHEMA_PATH", default_schema_path)
        
        # Load schema
        self._schema = self._load_schema()
        
        # Connection is created when needed
        self._connection = None
    
    def _load_schema(self) -> Dict[str, Any]:
        """
        Load database schema
        
        Returns:
            Schema dictionary
        """
        try:
            with open(self.schema_path, 'r') as schema_file:
                return json.load(schema_file)
        except Exception:
            # Return empty schema if file not found
            return {
                "tables": {},
                "views": {},
                "relationships": []
            }
    
    def _get_connection(self):
        """
        Get database connection
        
        Returns:
            Database connection
        """
        if self._connection is None or not self._connection.open:
            self._connection = pymysql.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database,
                cursorclass=pymysql.cursors.DictCursor
            )
        
        return self._connection
    
    def process(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a SWDP-related request
        
        Args:
            request: The request to process
            
        Returns:
            Response dictionary
        """
        if not self.validate_request(request):
            return {"success": False, "error": "Invalid request format"}
        
        action = request.get("action", "")
        
        if action == "execute_query":
            return self.execute_query(
                request.get("query", ""),
                request.get("params", {})
            )
        elif action == "get_table_schema":
            return self.get_table_schema(request.get("table", ""))
        elif action == "get_full_schema":
            return self.get_full_schema()
        elif action == "get_table_data":
            return self.get_table_data(
                request.get("table", ""),
                request.get("limit", 100),
                request.get("offset", 0),
                request.get("where", "")
            )
        elif action == "find_related_data":
            return self.find_related_data(
                request.get("table", ""),
                request.get("column", ""),
                request.get("value", ""),
                request.get("relationship_depth", 1)
            )
        else:
            return {"success": False, "error": f"Unsupported action: {action}"}
    
    def get_capabilities(self) -> List[str]:
        """
        Get the capabilities of this agent
        
        Returns:
            List of capability strings
        """
        return [
            "execute_query",
            "get_table_schema",
            "get_full_schema",
            "get_table_data",
            "find_related_data"
        ]
    
    def validate_request(self, request: Dict[str, Any]) -> bool:
        """
        Validate if a request can be processed by this agent
        
        Args:
            request: The request to validate
            
        Returns:
            True if the request is valid, False otherwise
        """
        if not isinstance(request, dict):
            return False
        
        if "action" not in request:
            return False
        
        action = request.get("action", "")
        
        if action not in self.get_capabilities():
            return False
        
        # Specific validations
        if action == "execute_query" and "query" not in request:
            return False
        
        if action == "get_table_schema" and "table" not in request:
            return False
        
        if action == "get_table_data" and "table" not in request:
            return False
        
        if action == "find_related_data" and (
            "table" not in request or
            "column" not in request or
            "value" not in request
        ):
            return False
        
        return True
    
    def authenticate(self) -> bool:
        """
        Authenticate with the database
        
        Returns:
            True if authentication was successful, False otherwise
        """
        try:
            connection = self._get_connection()
            return connection.open
        except Exception:
            return False
    
    def get_service_info(self) -> Dict[str, Any]:
        """
        Get information about the database service
        
        Returns:
            Service information
        """
        try:
            connection = self._get_connection()
            cursor = connection.cursor()
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()["VERSION()"]
            
            cursor.execute("SELECT DATABASE()")
            current_db = cursor.fetchone()["DATABASE()"]
            
            cursor.execute("SHOW TABLES")
            tables = [row[f"Tables_in_{current_db}"] for row in cursor.fetchall()]
            
            return {
                "success": True,
                "data": {
                    "version": version,
                    "database": current_db,
                    "host": self.host,
                    "port": self.port,
                    "tables": tables
                }
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def query(self, query_string: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute a database query
        
        Args:
            query_string: The query to execute
            params: Optional parameters for the query
            
        Returns:
            Query results
        """
        return self.execute_query(query_string, params)
    
    def get_schema(self) -> Dict[str, Any]:
        """
        Get the database schema
        
        Returns:
            Database schema information
        """
        return self.get_full_schema()
    
    def sanitize_query(self, query_string: str) -> str:
        """
        Sanitize a query string for safety
        
        Args:
            query_string: The query to sanitize
            
        Returns:
            Sanitized query string
        """
        # Basic sanitization - remove multiple semicolons and dangerous commands
        sanitized = query_string.strip()
        
        # Remove dangerous SQL commands
        dangerous_commands = [
            "DROP", "TRUNCATE", "DELETE", "UPDATE", "INSERT", "ALTER", "CREATE"
        ]
        
        if any(sanitized.upper().startswith(cmd) for cmd in dangerous_commands):
            raise ValueError(f"Dangerous SQL command detected: {sanitized}")
        
        # Further sanitization could be implemented here
        return sanitized
    
    def execute_query(self, query_string: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute a database query
        
        Args:
            query_string: Query to execute
            params: Parameters for the query
            
        Returns:
            Query results
        """
        try:
            # Sanitize query
            sanitized_query = self.sanitize_query(query_string)
            
            # Use empty dict if params is None
            params_dict = params or {}
            
            # Execute query
            connection = self._get_connection()
            cursor = connection.cursor()
            cursor.execute(sanitized_query, params_dict)
            
            # Get results
            if sanitized_query.strip().upper().startswith("SELECT"):
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
                # For non-SELECT queries
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
    
    def get_table_schema(self, table: str) -> Dict[str, Any]:
        """
        Get schema for a specific table
        
        Args:
            table: Table name
            
        Returns:
            Table schema
        """
        try:
            # First check if table exists in loaded schema
            if table in self._schema.get("tables", {}):
                return {
                    "success": True,
                    "data": self._schema["tables"][table]
                }
            
            # If not, get it from database
            connection = self._get_connection()
            cursor = connection.cursor()
            
            # Query for table columns
            cursor.execute(
                """
                SELECT 
                    COLUMN_NAME, 
                    DATA_TYPE, 
                    CHARACTER_MAXIMUM_LENGTH,
                    IS_NULLABLE,
                    COLUMN_KEY, 
                    EXTRA, 
                    COLUMN_COMMENT
                FROM 
                    INFORMATION_SCHEMA.COLUMNS 
                WHERE 
                    TABLE_SCHEMA = %s 
                    AND TABLE_NAME = %s
                ORDER BY 
                    ORDINAL_POSITION
                """,
                (self.database, table)
            )
            
            columns = []
            for row in cursor.fetchall():
                columns.append({
                    "name": row["COLUMN_NAME"],
                    "type": row["DATA_TYPE"],
                    "length": row["CHARACTER_MAXIMUM_LENGTH"],
                    "nullable": row["IS_NULLABLE"] == "YES",
                    "key": row["COLUMN_KEY"],
                    "extra": row["EXTRA"],
                    "comment": row["COLUMN_COMMENT"]
                })
            
            # Query for table indexes
            cursor.execute(
                """
                SELECT 
                    INDEX_NAME,
                    COLUMN_NAME,
                    NON_UNIQUE,
                    SEQ_IN_INDEX
                FROM 
                    INFORMATION_SCHEMA.STATISTICS
                WHERE 
                    TABLE_SCHEMA = %s 
                    AND TABLE_NAME = %s
                ORDER BY 
                    INDEX_NAME, SEQ_IN_INDEX
                """,
                (self.database, table)
            )
            
            indexes = {}
            for row in cursor.fetchall():
                index_name = row["INDEX_NAME"]
                if index_name not in indexes:
                    indexes[index_name] = {
                        "name": index_name,
                        "unique": row["NON_UNIQUE"] == 0,
                        "columns": []
                    }
                
                indexes[index_name]["columns"].append(row["COLUMN_NAME"])
            
            # Update schema
            table_schema = {
                "name": table,
                "columns": columns,
                "indexes": list(indexes.values())
            }
            
            # Save to schema cache
            if "tables" not in self._schema:
                self._schema["tables"] = {}
            
            self._schema["tables"][table] = table_schema
            
            return {
                "success": True,
                "data": table_schema
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_full_schema(self) -> Dict[str, Any]:
        """
        Get full database schema
        
        Returns:
            Full database schema
        """
        try:
            connection = self._get_connection()
            cursor = connection.cursor()
            
            # Get all tables
            cursor.execute("SHOW TABLES")
            tables = [row[f"Tables_in_{self.database}"] for row in cursor.fetchall()]
            
            schema = {
                "tables": {},
                "views": {},
                "relationships": []
            }
            
            # Get schema for each table
            for table in tables:
                result = self.get_table_schema(table)
                if result["success"]:
                    schema["tables"][table] = result["data"]
            
            # Get relationships
            cursor.execute(
                """
                SELECT
                    CONSTRAINT_NAME,
                    TABLE_NAME,
                    COLUMN_NAME,
                    REFERENCED_TABLE_NAME,
                    REFERENCED_COLUMN_NAME
                FROM
                    INFORMATION_SCHEMA.KEY_COLUMN_USAGE
                WHERE
                    REFERENCED_TABLE_SCHEMA = %s
                    AND REFERENCED_TABLE_NAME IS NOT NULL
                    AND TABLE_SCHEMA = %s
                """,
                (self.database, self.database)
            )
            
            for row in cursor.fetchall():
                schema["relationships"].append({
                    "name": row["CONSTRAINT_NAME"],
                    "table": row["TABLE_NAME"],
                    "column": row["COLUMN_NAME"],
                    "referenced_table": row["REFERENCED_TABLE_NAME"],
                    "referenced_column": row["REFERENCED_COLUMN_NAME"]
                })
            
            # Update schema cache
            self._schema = schema
            
            return {
                "success": True,
                "data": schema
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_table_data(
        self,
        table: str,
        limit: int = 100,
        offset: int = 0,
        where: str = ""
    ) -> Dict[str, Any]:
        """
        Get data from a table
        
        Args:
            table: Table name
            limit: Maximum number of rows to return
            offset: Offset for pagination
            where: WHERE clause
            
        Returns:
            Table data
        """
        try:
            # Build query
            query = f"SELECT * FROM {table}"
            
            # Add WHERE clause if provided
            if where:
                query += f" WHERE {where}"
            
            # Add LIMIT and OFFSET
            query += f" LIMIT {limit} OFFSET {offset}"
            
            # Execute query
            return self.execute_query(query)
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def find_related_data(
        self,
        table: str,
        column: str,
        value: Any,
        relationship_depth: int = 1
    ) -> Dict[str, Any]:
        """
        Find related data across tables
        
        Args:
            table: Starting table
            column: Column to search
            value: Value to search for
            relationship_depth: How deep to follow relationships
            
        Returns:
            Related data
        """
        try:
            results = {}
            
            # Get direct matches
            query = f"SELECT * FROM {table} WHERE {column} = %s"
            connection = self._get_connection()
            cursor = connection.cursor()
            cursor.execute(query, (value,))
            direct_matches = cursor.fetchall()
            
            results[table] = direct_matches
            
            # Get relationship info if needed
            if relationship_depth > 0 and self._schema.get("relationships"):
                # Find tables that reference this table
                referencing_relationships = [
                    rel for rel in self._schema["relationships"]
                    if rel["referenced_table"] == table and rel["referenced_column"] == column
                ]
                
                # Find tables that this table references
                referenced_relationships = [
                    rel for rel in self._schema["relationships"]
                    if rel["table"] == table
                ]
                
                # Follow references
                for rel in referencing_relationships:
                    ref_table = rel["table"]
                    ref_column = rel["column"]
                    
                    query = f"SELECT * FROM {ref_table} WHERE {ref_column} = %s"
                    cursor.execute(query, (value,))
                    ref_matches = cursor.fetchall()
                    
                    results[f"{ref_table} (referencing)"] = ref_matches
                
                # If there are direct matches, follow their references
                if direct_matches and relationship_depth > 1:
                    for rel in referenced_relationships:
                        ref_table = rel["referenced_table"]
                        ref_column = rel["referenced_column"]
                        source_column = rel["column"]
                        
                        # Get values for the source column
                        source_values = [row[source_column] for row in direct_matches if source_column in row]
                        
                        if source_values:
                            placeholders = ", ".join(["%s"] * len(source_values))
                            query = f"SELECT * FROM {ref_table} WHERE {ref_column} IN ({placeholders})"
                            cursor.execute(query, source_values)
                            ref_matches = cursor.fetchall()
                            
                            results[f"{ref_table} (referenced)"] = ref_matches
            
            return {"success": True, "data": results}
        except Exception as e:
            return {"success": False, "error": str(e)}