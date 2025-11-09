"""
Data Storage Module
Handles local persistence using CSV/Parquet with Delta Lake integration templates.
"""

import os
import pandas as pd
from datetime import datetime
from typing import List, Dict, Optional
import json


class DataStorage:
    """
    Data storage handler with local CSV/Parquet support and Delta Lake templates.
    
    PRODUCTION DELTA LAKE SETUP:
    1. Install delta-spark: pip install delta-spark pyspark
    2. Set delta_lake_enabled=true in config
    3. Configure delta_table_path (S3, Azure, HDFS, or local path)
    4. Uncomment Delta Lake code sections below
    """
    
    def __init__(self, storage_config: Dict):
        """
        Initialize data storage.
        
        Args:
            storage_config: Storage configuration from config file
        """
        self.config = storage_config
        self.local_mode = storage_config.get("local_mode", True)
        self.format = storage_config.get("format", "parquet")
        self.delta_enabled = storage_config.get("delta_lake_enabled", False)
        
        # Ensure data directory exists
        os.makedirs("data", exist_ok=True)
        
        # Initialize Delta Lake if enabled
        if self.delta_enabled:
            self._init_delta_lake()
    
    def _init_delta_lake(self):
        """
        Initialize Delta Lake (Spark-based distributed storage).
        
        PRODUCTION CODE - Uncomment when ready:
        Requires: pip install delta-spark pyspark
        """
        # PRODUCTION CODE - Uncomment for Delta Lake. We attempt imports only when
        # delta is enabled. If required packages are missing, print a helpful message
        # and fall back to local storage.
        try:
            from pyspark.sql import SparkSession  # type: ignore
            from delta import configure_spark_with_delta_pip  # type: ignore
        except Exception as e:
            print(f"⚠ Delta Lake libraries (pyspark/delta) not available: {e}. Using local file storage.")
            return

        try:
            builder = SparkSession.builder \
                .appName("TriageAI") \
                .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
                .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")

            self.spark = configure_spark_with_delta_pip(builder).getOrCreate()
            self.delta_table_path = self.config.get("delta_table_path", "data/delta_tables/tickets")

            print(f"✓ Delta Lake initialized: {self.delta_table_path}")
        except Exception as e:
            print(f"⚠ Failed to initialize Delta Lake runtime: {e}. Using local file storage.")
    
    def save_tickets(self, tickets: List[Dict], filename: Optional[str] = None) -> str:
        """
        Save tickets to storage.
        
        Args:
            tickets: List of ticket dictionaries
            filename: Optional filename (auto-generated if not provided)
            
        Returns:
            Path to saved file
        """
        if not tickets:
            print("⚠ No tickets to save")
            return ""
        
        # Convert to DataFrame
        df = pd.DataFrame(tickets)
        
        # Generate filename if not provided
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"tickets_{timestamp}"
        
        if self.delta_enabled:
            return self._save_to_delta(df, filename)
        else:
            return self._save_to_local(df, filename)
    
    def _save_to_local(self, df: pd.DataFrame, filename: str) -> str:
        """
        Save to local file system (CSV or Parquet).
        
        Args:
            df: DataFrame to save
            filename: Base filename
            
        Returns:
            Path to saved file
        """
        if self.format == "parquet":
            filepath = f"data/{filename}.parquet"
            df.to_parquet(filepath, index=False)
        else:  # CSV
            filepath = f"data/{filename}.csv"
            df.to_csv(filepath, index=False)
        
        print(f"✓ Tickets saved to {filepath}")
        return filepath
    
    def _save_to_delta(self, df: pd.DataFrame, filename: str) -> str:
        """
        Save to Delta Lake table.
        
        PRODUCTION CODE - Uncomment when Delta Lake is enabled.
        
        Args:
            df: DataFrame to save
            filename: Table name/path
            
        Returns:
            Path to Delta table
        """
        # PRODUCTION CODE - Uncomment for Delta Lake:
        """
        spark_df = self.spark.createDataFrame(df)
        
        # Write to Delta Lake with merge support
        spark_df.write \
            .format("delta") \
            .mode("append") \
            .option("mergeSchema", "true") \
            .save(self.delta_table_path)
        
        print(f"✓ Tickets saved to Delta table: {self.delta_table_path}")
        return self.delta_table_path
        """
        
        # Fallback to local storage
        print("⚠ Delta Lake not enabled, saving to local storage")
        return self._save_to_local(df, filename)
    
    def load_tickets(self, filename: Optional[str] = None) -> List[Dict]:
        """
        Load tickets from storage.
        
        Args:
            filename: Optional filename to load (loads most recent if not provided)
            
        Returns:
            List of ticket dictionaries
        """
        if self.delta_enabled:
            return self._load_from_delta()
        else:
            return self._load_from_local(filename)
    
    def _load_from_local(self, filename: Optional[str] = None) -> List[Dict]:
        """
        Load from local file system.
        
        Args:
            filename: Filename to load (with or without extension)
            
        Returns:
            List of ticket dictionaries
        """
        if not filename:
            # Find most recent file
            files = [f for f in os.listdir("data") if f.startswith("tickets_")]
            if not files:
                print("⚠ No saved tickets found")
                return []
            filename = sorted(files)[-1]
        
        filepath = f"data/{filename}" if "/" not in filename else filename
        
        try:
            if filepath.endswith(".parquet"):
                df = pd.read_parquet(filepath)
            else:
                df = pd.read_csv(filepath)
            
            print(f"✓ Loaded {len(df)} tickets from {filepath}")
            return df.to_dict('records')
        except Exception as e:
            print(f"⚠ Error loading tickets: {e}")
            return []
    
    def _load_from_delta(self) -> List[Dict]:
        """
        Load from Delta Lake table.
        
        PRODUCTION CODE - Uncomment when Delta Lake is enabled.
        
        Returns:
            List of ticket dictionaries
        """
        # PRODUCTION CODE - Uncomment for Delta Lake:
        """
        try:
            spark_df = self.spark.read.format("delta").load(self.delta_table_path)
            df = spark_df.toPandas()
            print(f"✓ Loaded {len(df)} tickets from Delta table")
            return df.to_dict('records')
        except Exception as e:
            print(f"⚠ Error loading from Delta Lake: {e}")
            return []
        """
        
        # Fallback to local storage
        print("⚠ Delta Lake not enabled, loading from local storage")
        return self._load_from_local()
    
    def get_latest_tickets(self, limit: int = 100) -> List[Dict]:
        """
        Get most recent tickets.
        
        Args:
            limit: Maximum number of tickets to return
            
        Returns:
            List of recent ticket dictionaries
        """
        tickets = self.load_tickets()
        return tickets[-limit:] if len(tickets) > limit else tickets
    
    def append_log(self, log_entry: Dict):
        """
        Append an action log entry.
        
        Args:
            log_entry: Log entry dictionary
        """
        log_file = "logs/triage_actions.log"
        os.makedirs("logs", exist_ok=True)
        
        with open(log_file, "a") as f:
            timestamp = datetime.now().isoformat()
            log_entry["timestamp"] = timestamp
            f.write(json.dumps(log_entry) + "\n")
            
    def log_assignment(self, ticket_id: str, engineer: str, is_fallback: bool, reason: str):
        """
        Log an assignment event to the audit log
        
        Args:
            ticket_id: Identifier of the ticket
            engineer: Name of the assigned engineer
            is_fallback: Whether this was a fallback assignment
            reason: Reason for fallback if applicable
        """
        log_file = "data/reassign_log.parquet"
        
        # Create DataFrame for new entry
        new_entry = pd.DataFrame([{
            "timestamp": datetime.now(),
            "ticket_id": ticket_id,
            "assigned_engineer": engineer,
            "is_fallback": is_fallback,
            "reason": reason
        }])
        
        # Append or create log file
        if os.path.exists(log_file):
            existing_df = pd.read_parquet(log_file)
            updated_df = pd.concat([existing_df, new_entry], ignore_index=True)
        else:
            updated_df = new_entry
            
        # Save to parquet
        updated_df.to_parquet(log_file, index=False)


# For testing this module independently
if __name__ == "__main__":
    from mock_data import MockDataGenerator
    
    print("=" * 80)
    print("DATA STORAGE TEST")
    print("=" * 80)
    
    # Generate sample tickets
    generator = MockDataGenerator()
    tickets = generator.generate_all_tickets(servicenow_count=5, jira_count=3)
    
    # Initialize storage
    storage_config = {
        "local_mode": True,
        "format": "parquet",
        "delta_lake_enabled": False
    }
    storage = DataStorage(storage_config)
    
    # Save tickets
    print("\nSaving tickets...")
    filepath = storage.save_tickets(tickets, "test_tickets")
    
    # Load tickets
    print("\nLoading tickets...")
    loaded_tickets = storage.load_tickets("test_tickets.parquet")
    print(f"Loaded {len(loaded_tickets)} tickets")
    
    # Test logging
    print("\nTesting action log...")
    storage.append_log({
        "action": "test",
        "tickets_processed": len(tickets),
        "status": "success"
    })
    print("✓ Log entry added")
