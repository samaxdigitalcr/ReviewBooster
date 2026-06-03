from database import SessionLocal, get_all_invitations
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
# Asegúrate de importar tus funciones de base de datos correctamente
from database import get_all_invitations 

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Configuración básica (asegúrate de tener esto definido en tu código)
BUSINESS_NAME = "Samax Digital" 

@app.get("/", response_class=HTMLResponse)
async def serve_dashboard(request: Request):
    try:
        # Obtenemos los registros desde la base de datos
        invitations = get_all_invitations(1) 
        
        # Calculamos las estadísticas para las 4 celdas del nuevo dashboard
        stats = {
            "total": len(invitations),
            "success": len([i for i in invitations if i.status == "Success"]),
            "failed": len([i for i in invitations if i.status != "Success"]),
            "sinpe": len([i for i in invitations if i.is_sinpe])
        }
        
    except Exception as e:
        print(f"Error cargando dashboard: {e}")
        # En caso de error, devolvemos ceros para no romper la interfaz
        stats = {"total": 0, "success": 0, "failed": 0, "sinpe": 0}
    
    return templates.TemplateResponse(
    request=request,
    name="index.html",
    context={
        "request": request,
        "stats": stats,
        "business_name": BUSINESS_NAME
    }
)

@app.get("/logs", response_class=HTMLResponse)
async def serve_logs(request: Request):
    # Obtenemos el historial completo
    invitations = get_all_invitations(1)
    
    return templates.TemplateResponse(
    request=request,
    name="logs.html",
    context={
        "request": request,
        "history": invitations,
        "business_name": BUSINESS_NAME
    }
)

@app.get("/analytics", response_class=HTMLResponse)
async def serve_analytics(request: Request):
    # Reutilizamos la lógica de cálculo (podrías crear una función helper para esto luego)
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
    context={
        "request": request, 
        "stats": stats, 
        "business_name": BUSINESS_NAME
    }
)

@app.post("/api/send-request")
async def send_review_request(request: Request):
    data = await request.json()
    
    # --- MODO DETECTIVE ---
    print(f"DEBUG: Datos recibidos desde el front: {data}")
    # ----------------------
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
