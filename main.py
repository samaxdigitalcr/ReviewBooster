import os
import re
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from twilio.rest import Client
from dotenv import load_dotenv
from database import init_db, log_invitation, get_all_invitations

# ==========================================
# 1. SETUP & CONFIGURATION
# ==========================================

# Load environment variables from the configuration file
load_dotenv()

app = FastAPI(title="Review Booster")

# Allow communication from any frontend origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Run database setup on startup
try:
    init_db()
except Exception as e:
    print(f"[DB Init Warning]: {e}")

# Point to the HTML template folder
templates = Jinja2Templates(directory="templates")

# Retrieve Twilio and Business credentials from environment variables
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER")
BUSINESS_NAME = os.getenv("BUSINESS_NAME", "Our Business")

# Initialize Twilio Client
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# ==========================================
# 2. DATA MODELS & UTILITIES
# ==========================================

class ReviewRequest(BaseModel):
    """Schema for validating incoming review invitation requests."""
    customer_name: str
    customer_phone: str
    review_url: str
    is_sinpe_payment: bool = False

def normalize_cr_phone(phone_str: str) -> str:
    # Strip everything that isn't a digit
    cleaned = re.sub(r'\D', '', phone_str)
    # If they included 506, remove it for the check
    if cleaned.startswith('506'):
        cleaned = cleaned[3:]
    # Now validate length
    if len(cleaned) != 8:
        raise ValueError("El número debe tener 8 dígitos.")
    return f"+506{cleaned}"

# ==========================================
# 3. ROUTES & API ENDPOINTS
# ==========================================

@app.get("/", response_class=HTMLResponse)
async def serve_dashboard(request: Request):
    """Serves the main dashboard and displays past invitation history."""
    try:
        history = get_all_invitations(1)
    except Exception:
        history = []
    template = templates.env.get_template("index.html")
    return HTMLResponse(content=template.render({
    "request": request, 
    "history": history, 
    "business_name": BUSINESS_NAME
}))

@app.post("/api/send-request")
async def send_review_request(request: ReviewRequest):
    """Handles the review invitation request and WhatsApp transmission."""
    
    # 1. Format phone number
    clean_phone = normalize_cr_phone(request.customer_phone)
    
    # 2. Select appropriate message based on payment method
    if request.is_sinpe_payment:
        msg = (f"¡Hola {request.customer_name}! Confirmamos tu pago por SINPE en {BUSINESS_NAME}. "
               f"¡Muchas gracias! ¿Nos cuentas qué tal estuvo tu experiencia aquí? {request.review_url}")
    else:
        msg = (f"Hi {request.customer_name}! Thanks for choosing {BUSINESS_NAME}. "
               f"We would love to hear about your experience: {request.review_url}")

    # 3. Send message via Twilio
    message = client.messages.create(
        from_=TWILIO_WHATSAPP_NUMBER, 
        to=f"whatsapp:{clean_phone}", 
        body=msg
    )
    
    # 4. Save the invitation record to the local database
    log_invitation(1, request.customer_name, clean_phone, request.review_url, "Success", request.is_sinpe_payment, message.sid)
    
    return {"success": True}