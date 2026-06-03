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
            "stats": stats, 
            "business_name": BUSINESS_NAME
        }
    )

@app.get("/logs", response_class=HTMLResponse)
async def serve_logs(request: Request):
    # Aquí cargaremos el historial completo para la página 2
    return templates.TemplateResponse("logs.html", {"request": request, "business_name": BUSINESS_NAME})

@app.get("/analytics", response_class=HTMLResponse)
async def serve_analytics(request: Request):
    # Aquí cargaremos los datos para las gráficas en la página 3
    return templates.TemplateResponse("analytics.html", {"request": request, "business_name": BUSINESS_NAME})
