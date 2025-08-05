# /database_models/manager.py (Final, Perfected Version)

import logging
import os
from contextlib import asynccontextmanager
from datetime import datetime
from typing import AsyncGenerator

from dotenv import load_dotenv
from sqlalchemy import (Column, BigInteger, DateTime, ForeignKey, Integer, JSON,
                        MetaData, Numeric, String, Table)
from sqlalchemy.ext.asyncio import (AsyncSession, create_async_engine)
from sqlalchemy.orm import sessionmaker

# --- 1. Setup & Configuration ---
# It's good practice to set up logging for your database module.
logger = logging.getLogger(__name__)

# Load environment variables from a .env file (primarily for local development)
load_dotenv()

# Get the database URL from environment variables.
DATABASE_URL = os.getenv("DATABASE_URL")

# --- 2. Database Engine & Metadata ---
# A single metadata object will hold all our table definitions.
metadata = MetaData()

# Check if DATABASE_URL is set. If not, the application cannot connect to the DB.
# We create a placeholder engine to prevent an immediate crash, but log a critical error.
if not DATABASE_URL:
    logger.critical("DATABASE_URL environment variable is not set! Database connection will fail.")
    engine = None
    AsyncSessionLocal = None
else:
    # Create the asynchronous engine for connecting to PostgreSQL.
    # `pool_pre_ping` checks if connections are alive before using them, which is good for production.
    engine = create_async_engine(DATABASE_URL, pool_pre_ping=True)
    
    # Create a configured "AsyncSession" class. This is the factory for our sessions.
    AsyncSessionLocal = sessionmaker(
        bind=engine, class_=AsyncSession, expire_on_commit=False
    )


# --- 3. Table Definitions ---
# By defining our tables here, we create a single source of truth for our database schema.

users = Table(
    "users",
    metadata,
    Column("telegram_id", BigInteger, primary_key=True, comment="The user's unique Telegram ID."),
    Column("username", String, nullable=True, comment="The user's Telegram username (optional)."),
    Column("balance", Numeric(10, 2), nullable=False, default=0.00, comment="The user's current wallet balance."),
    Column("created_at", DateTime, default=datetime.utcnow, nullable=False),
)

games = Table(
    "games",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("creator_id", BigInteger, ForeignKey("users.telegram_id"), nullable=False),
    Column("opponent_id", BigInteger, ForeignKey("users.telegram_id"), nullable=True),
    Column("stake", Numeric(10, 2), nullable=False, comment="The amount each player stakes."),
    Column("pot", Numeric(10, 2), nullable=False, comment="The total prize pool (stake * 2)."),
    Column("win_condition", Integer, nullable=False, comment="Number of tokens needed to win (1, 2, or 4)."),
    Column("board_state", JSON, nullable=True, comment="The current state of the Ludo board."),
    Column("current_turn_id", BigInteger, nullable=True, comment="The Telegram ID of the player whose turn it is."),
    Column("last_action_timestamp", DateTime, nullable=True, comment="Timestamp of the last move, used for forfeit logic."),
    Column("status", String, nullable=False, default="lobby", comment="Game status: lobby, active, finished, forfeited."),
    Column("winner_id", BigInteger, ForeignKey("users.telegram_id"), nullable=True),
    Column("created_at", DateTime, default=datetime.utcnow, nullable=False),
    Column("updated_at", DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False),
)

transactions = Table(
    "transactions",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("user_id", BigInteger, ForeignKey("users.telegram_id"), nullable=False),
    Column("amount", Numeric(10, 2), nullable=False, comment="The value of the transaction."),
    Column("type", String, nullable=False, comment="Type: deposit, withdrawal, stake, prize."),
    Column("status", String, nullable=False, comment="Status: pending, completed, failed."),
    Column("chapa_tx_ref", String, nullable=True, unique=True, comment="Unique transaction reference from Chapa gateway."),
    Column("created_at", DateTime, default=datetime.utcnow, nullable=False),
)


# --- 4. Database Session Management ---
@asynccontextmanager
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Provides a managed database session for use in FastAPI dependencies.
    This ensures the session is always closed, even if errors occur.
    """
    if AsyncSessionLocal is None:
        raise ConnectionError("Database is not configured. Check DATABASE_URL.")
    
    session = AsyncSessionLocal()
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()


# --- 5. Database Initialization ---
async def init_db():
    """
    Connects to the database and creates all tables defined in our metadata.
    This is called by the `buildCommand` in `render.yaml`.
    """
    if engine is None:
        logger.error("Cannot initialize database because the engine is not available.")
        return
        
    async with engine.begin() as conn:
        logger.info("Dropping all tables for a clean start...")
        await conn.run_sync(metadata.drop_all) # Optional: Use for a clean slate on every deploy
        logger.info("Creating all tables...")
        await conn.run_sync(metadata.create_all)
        logger.info("Database tables created successfully.")

# This allows the script to be run directly from the command line (e.g., `python -m database_models.manager`)
if __name__ == "__main__":
    import asyncio
    logger.info("Running database initialization directly...")
    asyncio.run(init_db())