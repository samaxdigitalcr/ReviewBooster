import re
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from database import SessionLocal, get_all_invitations, Invitation

app = FastAPI()
templates = Jinja2Templates(directory="templates")

BUSINESS_NAME = "Samax Digital"

def normalize_cr_phone(phone_str: str) -> str:
    cleaned = re.sub(r'\D', '', phone_str)
    if cleaned.startswith('506'):
        cleaned = cleaned[3:]
    if len(cleaned) != 8:
        raise ValueError("El número debe tener 8 dígitos.")
    return f"+506{cleaned}"

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
        is_sinpe = data.get("is_sinpe")

        clean_phone = normalize_cr_phone(customer_phone)

        db = SessionLocal()
        try:
            new_invitation = Invitation(
                customer_name=customer_name,
                customer_phone=clean_phone,  # Corregido: coincide con database.py
                review_url=review_url,
                is_sinpe=is_sinpe,
                status="Pending"
            )
            db.add(new_invitation)
            db.commit()
        finally:
            db.close()

        return {"status": "success", "message": "Invitación enviada"}
        
    except Exception as e:
        print(f"Error en send_review_request: {str(e)}")
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})
