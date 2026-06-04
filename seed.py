# create_admin.py
from database import SessionLocal, Business
from security import get_password_hash

def create_first_shop():
    db = SessionLocal()
    # Verifica si ya existe
    exists = db.query(Business).filter(Business.email == "demo@samax.com").first()
    if exists:
        print("El negocio demo ya existe.")
        return
        
    password_encriptada = get_password_hash("puravida123") # Cambia esto
    
    nuevo_comercio = Business(
        name="Samax Digital Demo",
        email="demo@samax.com",
        hashed_password=password_encriptada,
        is_active=True
        # Dejamos twilio en NULL para que use por defecto tus Envs del sandbox
    )
    db.add(nuevo_comercio)
    db.commit()
    print("¡Comercio semilla creado con éxito! Login: demo@samax.com / puravida123")

if __name__ == "__main__":
    create_first_shop()
