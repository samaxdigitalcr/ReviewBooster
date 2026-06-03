import os
import re
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from twilio.rest import Client
# IMPORTANTE: Cambiamos a database_5
from database import init_db, log_invitation, get_all_invitations

# ==========================================
# 1. SETUP & CONFIGURATION
# ==========================================

# Render usa variables de entorno del sistema, no necesitamos load_dotenv() en producción
app = FastAPI(title="Review Booster")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ejecutar setup de la BD al iniciar
try:
    init_db()
    print("[DB] Tablas inicializadas correctamente.")
except Exception as e:
    print(f"[DB Init Error]: {e}")

templates = Jinja2Templates(directory="templates")

# Obtenemos las credenciales desde el entorno
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER")
BUSINESS_NAME = os.getenv("BUSINESS_NAME", "Nuestro Negocio")

# Inicializar cliente de Twilio
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# ==========================================
# 2. DATA MODELS & UTILITIES
# ==========================================

class ReviewRequest(BaseModel):
    customer_name: str
    customer_phone: str
    review_url: str
    is_sinpe_payment: bool = False

def normalize_cr_phone(phone_str: str) -> str:
    cleaned = re.sub(r'\D', '', phone_str)
    if cleaned.startswith('506'):
        cleaned = cleaned[3:]
    if len(cleaned) != 8:
        raise ValueError("El número debe tener 8 dígitos.")
    return f"+506{cleaned}"

# ==========================================
# 3. ROUTES & API ENDPOINTS
# ==========================================

@app.get("/", response_class=HTMLResponse)
async def serve_dashboard(request: Request):
    try:
        # business_id 1 por defecto
        history = get_all_invitations(1)
    except Exception:
        history = []
    
    return templates.TemplateResponse("index.html", {
        "request": request, 
        "history": history, 
        "business_name": BUSINESS_NAME
    })

@app.post("/api/send-request")
async def send_review_request(request: ReviewRequest):
    clean_phone = normalize_cr_phone(request.customer_phone)
    
    if request.is_sinpe_payment:
        msg = (f"¡Hola {request.customer_name}! Confirmamos tu pago por SINPE en {BUSINESS_NAME}. "
               f"¡Muchas gracias! ¿Nos cuentas qué tal estuvo tu experiencia aquí? {request.review_url}")
    else:
        msg = (f"Hi {request.customer_name}! Thanks for choosing {BUSINESS_NAME}. "
               f"We would love to hear about your experience: {request.review_url}")

    message = client.messages.create(
        from_=TWILIO_WHATSAPP_NUMBER, 
        to=f"whatsapp:{clean_phone}", 
        body=msg
    )
    
    log_invitation(1, request.customer_name, clean_phone, request.review_url, "Success", request.is_sinpe_payment, message.sid)
    
    return {"success": True}
