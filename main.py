import os
import re
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from twilio.rest import Client
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
# IMPORTANTE: Asegúrate de que database.py esté en la misma carpeta
from database import init_db, log_invitation, get_all_invitations, DATABASE_URL

# ==========================================
# 1. SETUP & CONFIGURATION
# ==========================================

# Configuración del motor con pool_pre_ping para evitar errores de conexión
engine = create_engine(
    DATABASE_URL, 
    pool_pre_ping=True, 
    pool_recycle=300, 
    pool_size=5,
    max_overflow=0
)

# Fábrica de sesiones
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

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
        raw_history = get_all_invitations(1)
        history = []
        for item in raw_history:
            if hasattr(item, "__dict__"):
                item_dict = vars(item).copy()
                item_dict.pop('_sa_instance_state', None) 
                history.append(item_dict)
            else:
                history.append(dict(item))
    except Exception as e:
        print(f"Error cargando historial: {e}")
        history = []
    
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "history": history,
            "business_name": BUSINESS_NAME
        }
    )

@app.post("/api/send-request")
async def send_review_request(request: ReviewRequest):
    db = SessionLocal() # Abrimos sesión
    try:
        clean_phone = normalize_cr_phone(request.customer_phone)
        
        if request.is_sinpe_payment:
            msg = (f"¡Hola {request.customer_name}! Confirmamos tu pago por SINPE en {BUSINESS_NAME}. "
                   f"¡Muchas gracias! ¿Nos cuentas qué tal estuvo tu experiencia aquí? {request.review_url}")
        else:
            msg = (f"Hi {request.customer_name}! Thanks for choosing {BUSINESS_NAME}. "
                   f"We would love to hear about your experience: {request.review_url}")

        # Enviar mensaje vía Twilio
        message = client.messages.create(
            from_=TWILIO_WHATSAPP_NUMBER, 
            to=f"whatsapp:{clean_phone}", 
            body=msg
        )
        
        # Registrar en la BD
        log_invitation(1, request.customer_name, clean_phone, request.review_url, "Success", request.is_sinpe_payment, message.sid)
        
        return {"success": True}
        
    except Exception as e:
        db.rollback()
        print(f"Error procesando solicitud: {e}")
        raise e
    finally:
        db.close() # Cierre obligatorio de la conexión
