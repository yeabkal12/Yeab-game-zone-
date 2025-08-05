# In /database_models/manager.py

users = Table(
    "users",
    metadata,
    Column("telegram_id", BigInteger, primary_key=True, comment="The user's unique Telegram ID."),
    Column("username", String, nullable=True, comment="The user's Telegram username (optional)."),
    
    # --- NEW COLUMNS ---
    Column("phone_number", String, nullable=True, unique=True, comment="The user's registered phone number."),
    Column("status", String, nullable=False, default="unregistered", comment="User status: unregistered, unverified, verified."),
    # -------------------

    Column("balance", Numeric(10, 2), nullable=False, default=0.00, comment="The user's current wallet balance."),
    Column("created_at", DateTime, default=datetime.utcnow, nullable=False),
)