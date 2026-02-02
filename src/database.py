"""
Database manager for storing flight price history
"""

import logging
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional, Any

logger = logging.getLogger(__name__)


class Database:
    """SQLite database manager for flight prices"""
    
    def __init__(self, db_path: str = "data/flights.db"):
        self.db_path = db_path
        self._ensure_database_exists()
        self._create_tables()
        logger.info(f"Database initialized: {db_path}")
    
    def _ensure_database_exists(self):
        """Create database directory if it doesn't exist"""
        db_dir = Path(self.db_path).parent
        db_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def _create_tables(self):
        """Create database tables if they don't exist"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Price checks table (detailed, recent data)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS price_checks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                route VARCHAR(10) NOT NULL,
                origin VARCHAR(3) NOT NULL,
                destination VARCHAR(3) NOT NULL,
                departure_date DATE NOT NULL,
                return_date DATE NOT NULL,
                trip_length INTEGER NOT NULL,
                price DECIMAL(10,2) NOT NULL,
                currency VARCHAR(3) NOT NULL,
                stops INTEGER NOT NULL,
                airlines TEXT,
                connections TEXT,
                checked_at TIMESTAMP NOT NULL,
                offer_data TEXT,
                INDEX idx_route_date (route, checked_at),
                INDEX idx_checked_at (checked_at)
            )
        """)
        
        # Daily statistics (aggregated data)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS daily_stats (
                date DATE NOT NULL,
                route VARCHAR(10) NOT NULL,
                min_price DECIMAL(10,2),
                max_price DECIMAL(10,2),
                avg_price DECIMAL(10,2),
                median_price DECIMAL(10,2),
                num_checks INTEGER,
                PRIMARY KEY (date, route)
            )
        """)
        
        # Monthly statistics (long-term aggregates)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS monthly_stats (
                month VARCHAR(7) NOT NULL,
                route VARCHAR(10) NOT NULL,
                min_price DECIMAL(10,2),
                avg_price DECIMAL(10,2),
                num_days INTEGER,
                PRIMARY KEY (month, route)
            )
        """)
        
        # Deals found (always keep these)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS deals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                route VARCHAR(10) NOT NULL,
                origin VARCHAR(3) NOT NULL,
                destination VARCHAR(3) NOT NULL,
                departure_date DATE NOT NULL,
                return_date DATE NOT NULL,
                price DECIMAL(10,2) NOT NULL,
                currency VARCHAR(3) NOT NULL,
                discount_percent DECIMAL(5,2),
                deal_quality VARCHAR(20),
                outbound_info TEXT,
                inbound_info TEXT,
                booking_link TEXT,
                found_at TIMESTAMP NOT NULL,
                notified BOOLEAN DEFAULT 0,
                INDEX idx_found_at (found_at)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def add_price_check(self, flight_data: Dict[str, Any]):
        """Add a new price check to the database"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            # Extract data
            route = f"{flight_data['origin']}-{flight_data['destination']}"
            
            cursor.execute("""
                INSERT INTO price_checks (
                    route, origin, destination, departure_date, return_date,
                    trip_length, price, currency, stops, airlines, connections,
                    checked_at, offer_data
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                route,
                flight_data['origin'],
                flight_data['destination'],
                flight_data['departure_date'],
                flight_data['return_date'],
                flight_data['trip_length'],
                flight_data['price'],
                flight_data['currency'],
                flight_data['stops'],
                ','.join(flight_data.get('airlines', [])),
                ','.join(flight_data.get('connections', [])),
                datetime.now(),
                str(flight_data.get('raw_offer', ''))
            ))
            
            conn.commit()
            logger.debug(f"Added price check: {route} - {flight_data['price']} {flight_data['currency']}")
            
        except Exception as e:
            logger.error(f"Error adding price check: {e}")
            conn.rollback()
        finally:
            conn.close()
    
    def add_deal(self, deal_data: Dict[str, Any]):
        """Record a deal that was found"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            route = f"{deal_data['origin']}-{deal_data['destination']}"
            
            cursor.execute("""
                INSERT INTO deals (
                    route, origin, destination, departure_date, return_date,
                    price, currency, discount_percent, deal_quality,
                    outbound_info, inbound_info, booking_link, found_at, notified
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                route,
                deal_data['origin'],
                deal_data['destination'],
                deal_data['departure_date'],
                deal_data['return_date'],
                deal_data['price'],
                deal_data['currency'],
                deal_data.get('discount_percent'),
                deal_data.get('deal_quality', 'good'),
                str(deal_data.get('outbound')),
                str(deal_data.get('inbound')),
                deal_data.get('booking_link'),
                datetime.now(),
                deal_data.get('notified', False)
            ))
            
            conn.commit()
            logger.info(f"Recorded deal: {route} - {deal_data['price']} {deal_data['currency']}")
            
        except Exception as e:
            logger.error(f"Error adding deal: {e}")
            conn.rollback()
        finally:
            conn.close()
    
    def get_price_statistics(
        self,
        route: str,
        days: int = 30
    ) -> Dict[str, float]:
        """Get price statistics for a route over the last N days"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        cursor.execute("""
            SELECT
                MIN(price) as min_price,
                MAX(price) as max_price,
                AVG(price) as avg_price,
                COUNT(*) as num_checks
            FROM price_checks
            WHERE route = ? AND checked_at > ?
        """, (route, cutoff_date))
        
        row = cursor.fetchone()
        conn.close()
        
        if row and row['num_checks'] > 0:
            return {
                'min': row['min_price'],
                'max': row['max_price'],
                'avg': row['avg_price'],
                'count': row['num_checks'],
                'period_days': days
            }
        
        return {
            'min': None,
            'max': None,
            'avg': None,
            'count': 0,
            'period_days': days
        }
    
    def get_recent_deals(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent deals found"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM deals
            ORDER BY found_at DESC
            LIMIT ?
        """, (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def cleanup_old_data(
        self,
        detailed_days: int = 30,
        aggregate_days: int = 365
    ):
        """
        Clean up old data and create aggregates
        
        Args:
            detailed_days: Keep detailed checks for this many days
            aggregate_days: Keep daily aggregates for this many days
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            # Aggregate old detailed data into daily stats
            cutoff_detailed = datetime.now() - timedelta(days=detailed_days)
            
            cursor.execute("""
                INSERT OR REPLACE INTO daily_stats
                SELECT
                    DATE(checked_at) as date,
                    route,
                    MIN(price) as min_price,
                    MAX(price) as max_price,
                    AVG(price) as avg_price,
                    AVG(price) as median_price,
                    COUNT(*) as num_checks
                FROM price_checks
                WHERE checked_at < ?
                GROUP BY DATE(checked_at), route
            """, (cutoff_detailed,))
            
            # Delete old detailed records
            cursor.execute("""
                DELETE FROM price_checks
                WHERE checked_at < ?
            """, (cutoff_detailed,))
            
            deleted_count = cursor.rowcount
            
            # Create monthly aggregates from old daily stats
            cutoff_aggregate = datetime.now() - timedelta(days=aggregate_days)
            
            cursor.execute("""
                INSERT OR REPLACE INTO monthly_stats
                SELECT
                    strftime('%Y-%m', date) as month,
                    route,
                    MIN(min_price) as min_price,
                    AVG(avg_price) as avg_price,
                    COUNT(*) as num_days
                FROM daily_stats
                WHERE date < ?
                GROUP BY strftime('%Y-%m', date), route
            """, (cutoff_aggregate,))
            
            # Delete old daily stats
            cursor.execute("""
                DELETE FROM daily_stats
                WHERE date < ?
            """, (cutoff_aggregate,))
            
            # Vacuum to reclaim space
            cursor.execute("VACUUM")
            
            conn.commit()
            logger.info(f"Cleanup complete: Removed {deleted_count} old price checks")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
            conn.rollback()
        finally:
            conn.close()
