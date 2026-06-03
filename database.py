import os
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base

# ==========================================
# 1. DATABASE CONFIGURATION
# ==========================================

# Obtenemos la URL de la base de datos desde las variables de entorno de Render
DATABASE_URL = os.getenv("DATABASE_URL")

# Creamos el motor de conexión para PostgreSQL
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ==========================================
# 2. MODELS
# ==========================================

class Invitation(Base):
    __tablename__ = "invitations"
    
    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(Integer, default=1)
    customer_name = Column(String, nullable=False)
    customer_phone = Column(String, nullable=False)
    review_url = Column(String)
    status = Column(String, nullable=False)
    twilio_sid = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    is_sinpe = Column(Boolean, default=False)

# ==========================================
# 3. DATABASE OPERATIONS
# ==========================================

def init_db():
    """Crea las tablas en la base de datos externa."""
    Base.metadata.create_all(bind=engine)

def log_invitation(business_id, name, phone, url, status, is_sinpe, sid=None):
    """Inserta una nueva invitación en PostgreSQL."""
    db = SessionLocal()
    try:
        new_entry = Invitation(
            business_id=business_id,
            customer_name=name,
            customer_phone=phone,
            review_url=url,
            status=status,
            twilio_sid=sid,
            is_sinpe=bool(is_sinpe)
        )
        db.add(new_entry)
        db.commit()
    finally:
        db.close()

def get_all_invitations(business_id):
    """Recupera todas las invitaciones de un negocio."""
    db = SessionLocal()
    try:
        rows = db.query(Invitation).filter(Invitation.business_id == business_id)\
                  .order_by(Invitation.timestamp.desc()).all()
        
        # Convertimos los objetos a diccionarios para que el resto de tu código no se rompa
        return [row.__dict__ for row in rows]
    finally:
        db.close()
