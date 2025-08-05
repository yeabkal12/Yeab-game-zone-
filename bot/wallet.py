# /bot/wallet.py (New Version with OTP and Chapa)

import os
import random
import requests
from decimal import Decimal

# --- Chapa Configuration ---
CHAPA_API_KEY = os.getenv("CHAPA_API_KEY")
CHAPA_API_URL = "https://api.chapa.co/v1"

# --- Placeholder OTP Service ---
# In a real application, you would use a real SMS provider API here.
def send_otp_sms(phone_number: str) -> str:
    """
    Sends an OTP to the given phone number.
    Returns the OTP code so we can save it for verification.
    """
    otp_code = str(random.randint(100000, 999999))
    print(f"--- SIMULATING OTP ---")
    print(f"--- Sending OTP {otp_code} to {phone_number} ---")
    print(f"--- (In production, a real SMS would be sent via an API) ---")
    return otp_code

# --- Chapa API Functions ---
def initiate_chapa_deposit(user_id: int, amount: Decimal, tx_ref: str) -> str | None:
    """Initializes a transaction with Chapa and returns the checkout URL."""
    headers = {"Authorization": f"Bearer {CHAPA_API_KEY}"}
    payload = {
        "amount": str(amount),
        "currency": "ETB",
        "email": f"{user_id}@yeabgame.zone",  # Placeholder email
        "first_name": "Player",
        "last_name": str(user_id),
        "tx_ref": tx_ref,
        "callback_url": f"{os.getenv('WEBHOOK_URL')}/api/chapa/callback",
        "return_url": f"https://t.me/{os.getenv('BOT_USERNAME')}", # Placeholder
    }
    
    try:
        response = requests.post(f"{CHAPA_API_URL}/transaction/initialize", headers=headers, json=payload)
        response.raise_for_status()
        return response.json()['data']['checkout_url']
    except requests.RequestException as e:
        print(f"Error initiating Chapa deposit: {e}")
        return None