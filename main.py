import os
import re
from fastapi import FastAPI, Request, Depends, HTTPException, status, Cookie
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordRequestForm
from twilio.rest import Client
# Asegúrate de que estos importes existan en database.py
from database import SessionLocal, get_all_invitations, Invitation, log_invitation, Business
from security import verify_access_token
from sqlalchemy.orm import Session

# Dependencia para la BD
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Dependencia para proteger rutas HTML
async def get_current_business(access_token: str = Cookie(None), db: Session = Depends(get_db)):
    if not access_token:
        raise HTTPException(status_code=status.HTTP_307_TEMPORARY_REDIRECT, headers={"Location": "/login"})
    
    payload = verify_access_token(access_token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_307_TEMPORARY_REDIRECT, headers={"Location": "/login"})
    
    business_id = payload.get("sub")
    business = db.query(Business).filter(Business.id == business_id).first()
    
    if not business or not business.is_active:
        raise HTTPException(status_code=status.HTTP_307_TEMPORARY_REDIRECT, headers={"Location": "/login"})
        
    return business # Retorna el objeto completo del comercio logueado



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
async def serve_dashboard(request: Request, current_business: Business = Depends(get_current_business), db: Session = Depends(get_db)):
    try:
        # Extraemos dinámicamente las invitaciones de ESTE comercio
        invitations = get_all_invitations(db, current_business.id)
        
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
        context={
            "request": request, 
            "stats": stats, 
            "business_name": current_business.name # Nombre dinámico desde la BD
        }
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
async def send_review_request(
    request: Request, 
    current_business: Business = Depends(get_current_business), 
    db: Session = Depends(get_db)
):
    try:
        data = await request.json()
        
        customer_name = data.get("customer_name")
        customer_phone = data.get("customer_phone")
        review_url = data.get("review_url")
        is_sinpe = data.get("is_sinpe")

        # De momento, simulamos que el negocio logueado es el ID 1
        current_business_id = 1 

        # 1. Buscar este negocio en la base de datos
        business = db.query(Business).filter(Business.id == current_business_id).first()
        if not business:
            return JSONResponse(status_code=404, content={"status": "error", "message": "Negocio no registrado"})

        # 2. Determinar qué credenciales usar (Las de él o tu Sandbox por defecto)
        account_sid = business.twilio_account_sid or os.getenv("TWILIO_ACCOUNT_SID")
        auth_token = business.twilio_auth_token or os.getenv("TWILIO_AUTH_TOKEN")
        whatsapp_number = business.twilio_whatsapp_number or os.getenv("TWILIO_WHATSAPP_NUMBER")
        business_name = business.name # Usamos el nombre real de la BD

        # 3. Inicializar Twilio dinámicamente
        dynamic_client = Client(account_sid, auth_token)

        # 4. Normalizar teléfono de Costa Rica
        clean_phone = normalize_cr_phone(customer_phone)

        # 5. Preparar mensaje
        if is_sinpe:
            msg = (f"¡Hola {customer_name}! Confirmamos tu pago por SINPE en {business_name}. "
                   f"¡Muchas gracias! ¿Nos cuentas qué tal estuvo tu experiencia aquí? {review_url}")
        else:
            msg = (f"Hi {customer_name}! Thanks for choosing {business_name}. "
                   f"We would love to hear about your experience: {review_url}")

        # 6. Enviar mensaje
        message = dynamic_client.messages.create(
            from_=whatsapp_number, 
            to=f"whatsapp:{clean_phone}", 
            body=msg
        )
        
        # 7. Registrar en la BD pasando la sesión 'db'
        log_invitation(db, current_business_id, customer_name, clean_phone, review_url, "Success", is_sinpe, message.sid)
        
        return {"status": "success", "message": "Invitación enviada y mensaje entregado"}
        
    except Exception as e:
        print(f"Error procesando solicitud: {e}")
        # Si falla el envío, intentamos registrar el fallo en el historial para que no se pierda la métrica
        try:
            log_invitation(db, current_business_id, customer_name, clean_phone, review_url, "Failed", is_sinpe, None)
        except:
            pass
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def login_process(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    # Buscamos por email (usamos form_data.username que es el estándar de FastAPI)
    business = db.query(Business).filter(Business.email == form_data.username).first()
    
    if not business or not verify_password(form_data.password, business.hashed_password):
        return templates.TemplateResponse("login.html", {"error": "Credenciales incorrectas"})
    
    # Generar token
    token = create_access_token(data={"sub": str(business.id)})
    
    # Redirigir al dashboard seteando la Cookie
    response = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    response.set_cookie(key="access_token", value=token, httponly=True)
    return response

@app.get("/logout")
async def logout():
    response = RedirectResponse(url="/login")
    response.delete_cookie("access_token")
    return response
