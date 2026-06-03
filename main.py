import os
import re
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from twilio.rest import Client
# Asegúrate de que estos importes existan en database.py
from database import SessionLocal, get_all_invitations, Invitation, log_invitation

app = FastAPI(title="Review Booster")

# Permitir CORS para comunicación con el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory="templates")

# ==========================================
# CONFIGURACIÓN TWILIO
# ==========================================
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER")
BUSINESS_NAME = os.getenv("BUSINESS_NAME", "Samax Digital")

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# ==========================================
# UTILIDADES
# ==========================================
def normalize_cr_phone(phone_str: str) -> str:
    cleaned = re.sub(r'\D', '', phone_str)
    if cleaned.startswith('506'):
        cleaned = cleaned[3:]
    if len(cleaned) != 8:
        raise ValueError("El número debe tener 8 dígitos.")
    return f"+506{cleaned}"

# ==========================================
# RUTAS
# ==========================================
@app.get("/", response_class=HTMLResponse)
async def serve_dashboard(request: Request):
    try:
        invitations = get_all_invitations(1)
        stats = {
            "total": len(invitations),
            "success": len([i for i in invitations if i.status == "Success"]),
            "failed": len([i for i in invitations if i.status != "Success"]),
            "sinpe": len([i for i in invitations if i.is_sinpe])
        }
    except Exception as e:
        print(f"Error cargando dashboard: {e}")
        stats = {"total": 0, "success": 0, "failed": 0, "sinpe": 0}
    
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"request": request, "stats": stats, "business_name": BUSINESS_NAME}
    )

@app.get("/logs", response_class=HTMLResponse)
async def serve_logs(request: Request):
    invitations = get_all_invitations(1)
    return templates.TemplateResponse(
        request=request,
        name="logs.html",
        context={"request": request, "history": invitations, "business_name": BUSINESS_NAME}
    )

@app.get("/analytics", response_class=HTMLResponse)
async def serve_analytics(request: Request):
    invitations = get_all_invitations(1)
    stats = {
        "total": len(invitations),
        "success": len([i for i in invitations if i.status == "Success"]),
        "failed": len([i for i in invitations if i.status != "Success"]),
        "sinpe": len([i for i in invitations if i.is_sinpe])
    }
    return templates.TemplateResponse(
        request=request,
        name="analytics.html",
        context={"request": request, "stats": stats, "business_name": BUSINESS_NAME}
    )

@app.post("/api/send-request")
async def send_review_request(request: Request):
    try:
        data = await request.json()
        
        customer_name = data.get("customer_name")
        customer_phone = data.get("customer_phone")
        review_url = data.get("review_url")
        is_sinpe = data.get("is_sinpe") # Asegúrate que tu JS envíe un booleano

        # 1. Normalizar teléfono
        clean_phone = normalize_cr_phone(customer_phone)

        # 2. Preparar mensaje
        if is_sinpe:
            msg = (f"¡Hola {customer_name}! Confirmamos tu pago por SINPE en {BUSINESS_NAME}. "
                   f"¡Muchas gracias! ¿Nos cuentas qué tal estuvo tu experiencia aquí? {review_url}")
        else:
            msg = (f"Hi {customer_name}! Thanks for choosing {BUSINESS_NAME}. "
                   f"We would love to hear about your experience: {review_url}")

        # 3. Enviar vía Twilio
        message = client.messages.create(
            from_=TWILIO_WHATSAPP_NUMBER, 
            to=f"whatsapp:{clean_phone}", 
            body=msg
        )
        
        # 4. Registrar en la BD (usando tu función log_invitation)
        log_invitation(1, customer_name, clean_phone, review_url, "Success", is_sinpe, message.sid)
        
        return {"status": "success", "message": "Invitación enviada y mensaje entregado"}
        
    except Exception as e:
        print(f"Error procesando solicitud: {e}")
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})
