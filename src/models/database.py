"""
Database integration module for the spending transaction monitor.

This module provides database connection management and utilities
for working with the Prisma ORM and PostgreSQL database.
"""

import asyncio
import logging
from typing import Optional, Dict, Any
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)

# Make Prisma import optional
try:
    from generated.prisma import Prisma
    PRISMA_AVAILABLE = True
except ImportError:
    PRISMA_AVAILABLE = False
    Prisma = None


class DatabaseManager:
    """Manages database connections and provides database utilities"""
    
    def __init__(self):
        self.prisma: Optional[Prisma] = None
        self._is_connected: bool = False
    
    async def connect(self) -> None:
        """Establish connection to the database"""
        if not PRISMA_AVAILABLE:
            logger.warning("Prisma not available, database operations will be disabled")
            return
            
        try:
            self.prisma = Prisma()
            await self.prisma.connect()
            self._is_connected = True
            logger.info("Database connection established successfully")
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise
    
    async def disconnect(self) -> None:
        """Close database connection"""
        if self.prisma and self._is_connected and PRISMA_AVAILABLE:
            try:
                await self.prisma.disconnect()
                self._is_connected = False
                logger.info("Database connection closed successfully")
            except Exception as e:
                logger.error(f"Error closing database connection: {e}")
    
    @property
    def is_connected(self) -> bool:
        """Check if database is connected"""
        return self._is_connected and PRISMA_AVAILABLE
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform database health check"""
        if not PRISMA_AVAILABLE:
            return {"status": "unavailable", "error": "Prisma not available"}
        
        if not self.is_connected:
            return {"status": "disconnected", "error": "Database not connected"}
        
        try:
            # Simple query to test connection
            await self.prisma.user.find_first()
            return {"status": "healthy", "message": "Database connection is working"}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}
    
    async def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        if not PRISMA_AVAILABLE:
            logger.warning("Database not available, returning None")
            return None
            
        if not self.is_connected:
            raise RuntimeError("Database not connected")
        
        try:
            user = await self.prisma.user.find_unique(
                where={"id": user_id},
                include={
                    "creditCards": True,
                    "alertRules": True
                }
            )
            return user
        except Exception as e:
            logger.error(f"Error fetching user {user_id}: {e}")
            return None
    
    async def get_transaction_by_id(self, transaction_id: str) -> Optional[Dict[str, Any]]:
        """Get transaction by ID"""
        if not PRISMA_AVAILABLE:
            logger.warning("Database not available, returning None")
            return None
            
        if not self.is_connected:
            raise RuntimeError("Database not connected")
        
        try:
            transaction = await self.prisma.transaction.find_unique(
                where={"id": transaction_id},
                include={
                    "user": True,
                    "creditCard": True
                }
            )
            return transaction
        except Exception as e:
            logger.error(f"Error fetching transaction {transaction_id}: {e}")
            return None
    
    async def get_user_rules(self, user_id: str) -> list:
        """Get all active rules for a user"""
        if not PRISMA_AVAILABLE:
            logger.warning("Database not available, returning empty list")
            return []
            
        if not self.is_connected:
            raise RuntimeError("Database not connected")
        
        try:
            rules = await self.prisma.alert_rule.find_many(
                where={
                    "userId": user_id,
                    "isActive": True
                }
            )
            return rules
        except Exception as e:
            logger.error(f"Error fetching rules for user {user_id}: {e}")
            return []
    
    async def create_transaction(self, transaction_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a new transaction"""
        if not PRISMA_AVAILABLE:
            logger.warning("Database not available, transaction not created")
            return None
            
        if not self.is_connected:
            raise RuntimeError("Database not connected")
        
        try:
            transaction = await self.prisma.transaction.create(data=transaction_data)
            return transaction
        except Exception as e:
            logger.error(f"Error creating transaction: {e}")
            return None
    
    async def update_user_location(self, user_id: str, location_data: Dict[str, Any]) -> bool:
        """Update user's location information"""
        if not PRISMA_AVAILABLE:
            logger.warning("Database not available, location not updated")
            return False
            
        if not self.is_connected:
            raise RuntimeError("Database not connected")
        
        try:
            await self.prisma.user.update(
                where={"id": user_id},
                data=location_data
            )
            return True
        except Exception as e:
            logger.error(f"Error updating user location for {user_id}: {e}")
            return False


# Global database manager instance
db_manager = DatabaseManager()


@asynccontextmanager
async def get_database():
    """Context manager for database operations"""
    if not db_manager.is_connected and PRISMA_AVAILABLE:
        await db_manager.connect()
    
    try:
        yield db_manager
    finally:
        # Don't disconnect here as it's a global instance
        pass


async def initialize_database():
    """Initialize database connection"""
    if PRISMA_AVAILABLE:
        await db_manager.connect()


async def cleanup_database():
    """Cleanup database connection"""
    await db_manager.disconnect() 