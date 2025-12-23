"""
Table analysis logic for determining fact/dimension types, keys, references, etc.
"""
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import psycopg2
from psycopg2.extras import RealDictCursor


class TableAnalyzer:
    """Analyzes database tables to determine their characteristics."""
    
    def __init__(self, db_uri: str):
        """
        Initialize the table analyzer.
        
        Args:
            db_uri: PostgreSQL database connection URI
        """
        self.db_uri = db_uri
    
    def _get_connection(self):
        """Get a database connection."""
        return psycopg2.connect(self.db_uri)
    
    def analyze_table(
        self, 
        schema_name: str, 
        table_name: str, 
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Perform comprehensive analysis of a table.
        
        Args:
            schema_name: Schema name
            table_name: Table name
            metadata: Table metadata from Postgres MCP (columns, constraints, indexes)
            
        Returns:
            Dictionary containing analysis results
        """
        conn = self._get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Get record count
                record_count = self._get_record_count(cur, schema_name, table_name)
                
                # Get daily load statistics
                daily_load = self._get_daily_load_stats(cur, schema_name, table_name, metadata)
                
                # Determine table type
                table_type = self._determine_table_type(metadata, cur, schema_name, table_name)
                
                # Identify primary key
                primary_key = self._identify_primary_key(metadata)
                
                # Identify foreign keys (references to dimensions)
                foreign_keys = self._identify_foreign_keys(metadata, cur, schema_name, table_name)
                
                # Identify dimension key (for dimension tables)
                dimension_key = None
                if table_type == "dimension":
                    dimension_key = self._identify_dimension_key(metadata, primary_key)
                
                return {
                    "schema": schema_name,
                    "table": table_name,
                    "table_type": table_type,
                    "record_count": record_count,
                    "daily_load": daily_load,
                    "primary_key": primary_key,
                    "foreign_keys": foreign_keys,
                    "dimension_key": dimension_key,
                    "columns": metadata.get("columns", []),
                    "constraints": metadata.get("constraints", []),
                    "indexes": metadata.get("indexes", [])
                }
        finally:
            conn.close()
    
    def _get_record_count(self, cursor, schema_name: str, table_name: str) -> int:
        """Get total record count for the table."""
        query = f'SELECT COUNT(*) as count FROM "{schema_name}"."{table_name}"'
        cursor.execute(query)
        result = cursor.fetchone()
        return result['count'] if result else 0
    
    def _get_daily_load_stats(
        self, 
        cursor, 
        schema_name: str, 
        table_name: str, 
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Get daily load statistics by analyzing timestamp columns.
        
        Returns:
            Dictionary with daily load information
        """
        # Find timestamp columns that might indicate when records were created
        timestamp_columns = self._find_timestamp_columns(metadata)
        
        if not timestamp_columns:
            return {
                "records_per_day": None,
                "last_load_date": None,
                "method": "no_timestamp_column"
            }
        
        # Use the first timestamp column found
        timestamp_col = timestamp_columns[0]['name']
        
        # Get records per day for the last 30 days
        query = f"""
            SELECT 
                DATE({timestamp_col}) as load_date,
                COUNT(*) as record_count
            FROM "{schema_name}"."{table_name}"
            WHERE {timestamp_col} >= CURRENT_DATE - INTERVAL '30 days'
            GROUP BY DATE({timestamp_col})
            ORDER BY load_date DESC
        """
        
        cursor.execute(query)
        daily_counts = cursor.fetchall()
        
        if not daily_counts:
            return {
                "records_per_day": 0,
                "last_load_date": None,
                "method": "timestamp_analysis"
            }
        
        # Calculate average records per day
        total_records = sum(row['record_count'] for row in daily_counts)
        days = len(daily_counts)
        avg_per_day = total_records / days if days > 0 else 0
        
        # Get most recent load date
        last_load_date = daily_counts[0]['load_date'] if daily_counts else None
        
        return {
            "records_per_day": round(avg_per_day, 2),
            "last_load_date": last_load_date.isoformat() if last_load_date else None,
            "daily_breakdown": [
                {
                    "date": row['load_date'].isoformat() if row['load_date'] else None,
                    "count": row['record_count']
                }
                for row in daily_counts[:7]  # Last 7 days
            ],
            "method": "timestamp_analysis",
            "timestamp_column_used": timestamp_col
        }
    
    def _find_timestamp_columns(self, metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find columns that are likely timestamp/date columns."""
        timestamp_types = [
            'timestamp', 'timestamp without time zone', 'timestamp with time zone',
            'date', 'timestamptz', 'timestampz'
        ]
        
        columns = metadata.get("columns", [])
        timestamp_cols = []
        
        for col in columns:
            col_type = str(col.get("data_type", "")).lower()
            col_name = col.get("name", "").lower()
            
            # Check if type matches or name suggests timestamp
            if any(ts_type in col_type for ts_type in timestamp_types):
                timestamp_cols.append(col)
            elif any(keyword in col_name for keyword in ['created', 'inserted', 'load', 'date', 'time']):
                timestamp_cols.append(col)
        
        return timestamp_cols
    
    def _determine_table_type(
        self, 
        metadata: Dict[str, Any], 
        cursor, 
        schema_name: str, 
        table_name: str
    ) -> str:
        """
        Determine if table is a fact table or dimension table.
        
        Logic:
        - Fact tables: Have foreign keys to dimension tables, typically transactional
        - Dimension tables: Referenced by fact tables, contain descriptive attributes
        """
        # Check for foreign keys
        foreign_keys = self._identify_foreign_keys(metadata, cursor, schema_name, table_name)
        
        # Check if this table is referenced by other tables (dimension characteristic)
        is_referenced = self._is_table_referenced(cursor, schema_name, table_name)
        
        # Heuristics:
        # - If has foreign keys and is referenced: likely dimension
        # - If has foreign keys and not referenced: likely fact
        # - If no foreign keys but is referenced: likely dimension
        # - If no foreign keys and not referenced: check column patterns
        
        if foreign_keys and is_referenced:
            return "dimension"  # Dimension tables are often referenced
        elif foreign_keys and not is_referenced:
            return "fact"  # Fact tables reference dimensions
        elif not foreign_keys and is_referenced:
            return "dimension"
        else:
            # Check column patterns
            columns = metadata.get("columns", [])
            # Fact tables often have numeric measures
            numeric_cols = sum(1 for col in columns 
                             if any(t in str(col.get("data_type", "")).lower() 
                                   for t in ['numeric', 'decimal', 'integer', 'bigint', 'double']))
            
            # If many numeric columns, likely fact table
            if numeric_cols > len(columns) * 0.3:
                return "fact"
            else:
                return "dimension"
    
    def _identify_primary_key(self, metadata: Dict[str, Any]) -> Optional[List[str]]:
        """Identify primary key columns from metadata."""
        constraints = metadata.get("constraints", [])
        
        for constraint in constraints:
            if constraint.get("constraint_type") == "PRIMARY KEY":
                return constraint.get("columns", [])
        
        return None
    
    def _identify_foreign_keys(
        self, 
        metadata: Dict[str, Any], 
        cursor, 
        schema_name: str, 
        table_name: str
    ) -> List[Dict[str, Any]]:
        """Identify foreign key relationships."""
        foreign_keys = []
        
        # Get foreign keys from metadata
        constraints = metadata.get("constraints", [])
        for constraint in constraints:
            if constraint.get("constraint_type") == "FOREIGN KEY":
                fk_info = {
                    "columns": constraint.get("columns", []),
                    "referenced_table": constraint.get("referenced_table"),
                    "referenced_columns": constraint.get("referenced_columns", []),
                    "constraint_name": constraint.get("name")
                }
                foreign_keys.append(fk_info)
        
        # Also query database for foreign keys if not in metadata
        if not foreign_keys:
            query = """
                SELECT
                    tc.constraint_name,
                    kcu.column_name,
                    ccu.table_schema AS foreign_table_schema,
                    ccu.table_name AS foreign_table_name,
                    ccu.column_name AS foreign_column_name
                FROM information_schema.table_constraints AS tc
                JOIN information_schema.key_column_usage AS kcu
                    ON tc.constraint_name = kcu.constraint_name
                    AND tc.table_schema = kcu.table_schema
                JOIN information_schema.constraint_column_usage AS ccu
                    ON ccu.constraint_name = tc.constraint_name
                    AND ccu.table_schema = tc.table_schema
                WHERE tc.constraint_type = 'FOREIGN KEY'
                    AND tc.table_schema = %s
                    AND tc.table_name = %s
            """
            cursor.execute(query, (schema_name, table_name))
            results = cursor.fetchall()
            
            # Group by constraint name
            fk_groups = {}
            for row in results:
                constraint_name = row['constraint_name']
                if constraint_name not in fk_groups:
                    fk_groups[constraint_name] = {
                        "columns": [],
                        "referenced_table": f"{row['foreign_table_schema']}.{row['foreign_table_name']}",
                        "referenced_columns": [],
                        "constraint_name": constraint_name
                    }
                fk_groups[constraint_name]["columns"].append(row['column_name'])
                fk_groups[constraint_name]["referenced_columns"].append(row['foreign_column_name'])
            
            foreign_keys = list(fk_groups.values())
        
        return foreign_keys
    
    def _is_table_referenced(self, cursor, schema_name: str, table_name: str) -> bool:
        """Check if this table is referenced by other tables (foreign keys pointing to it)."""
        query = """
            SELECT COUNT(*) as count
            FROM information_schema.table_constraints AS tc
            JOIN information_schema.constraint_column_usage AS ccu
                ON ccu.constraint_name = tc.constraint_name
                AND ccu.table_schema = tc.table_schema
            WHERE tc.constraint_type = 'FOREIGN KEY'
                AND ccu.table_schema = %s
                AND ccu.table_name = %s
        """
        cursor.execute(query, (schema_name, table_name))
        result = cursor.fetchone()
        return result['count'] > 0 if result else False
    
    def _identify_dimension_key(
        self, 
        metadata: Dict[str, Any], 
        primary_key: Optional[List[str]]
    ) -> Optional[Dict[str, Any]]:
        """
        Identify the dimension key (surrogate key or natural key).
        
        For dimension tables, the key is typically:
        - Primary key (surrogate key like id, key, dim_key)
        - Or a natural key (business key)
        """
        if primary_key:
            return {
                "type": "primary_key",
                "columns": primary_key,
                "key_type": "surrogate" if any(
                    col.lower() in ['id', 'key', 'dim_key', 'sk'] 
                    for col in primary_key
                ) else "natural"
            }
        
        # Look for common key column patterns
        columns = metadata.get("columns", [])
        for col in columns:
            col_name = col.get("name", "").lower()
            if col_name in ['id', 'key', 'dim_key', 'dimension_key', 'sk', 'surrogate_key']:
                return {
                    "type": "candidate_key",
                    "columns": [col.get("name")],
                    "key_type": "surrogate"
                }
        
        return None

