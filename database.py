import os
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base

# ==========================================
# 1. DATABASE CONFIGURATION
# ==========================================

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(
    DATABASE_URL, 
    pool_pre_ping=True, 
    pool_recycle=300
)
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

def log_invitation(business_id, name, phone, url, status, is_sinpe, sid):
    # Intentamos guardar hasta 2 veces
    for attempt in range(2):
        db = SessionLocal()
        try:
            # CORRECCIÓN: Pasamos los valores usando los nombres de las columnas
            new_invite = Invitation(
                business_id=business_id,
                customer_name=name,
                customer_phone=phone,
                review_url=url,
                status=status,
                twilio_sid=sid,
                is_sinpe=is_sinpe,
                timestamp=datetime.utcnow()
            )
            db.add(new_invite)
            db.commit()
            return # Si sale bien, salimos de la función
        except Exception as e:
            db.rollback()
            if attempt == 0: 
                print(f"Intento 1 fallido, reintentando... Error: {e}")
                continue
            else:
                print(f"Error crítico en BD tras reintento: {e}")
                raise e
        finally:
            db.close()

def get_all_invitations(business_id):
    """Recupera todas las invitaciones de un negocio."""
    db = SessionLocal()
    try:
        return db.query(Invitation).filter(Invitation.business_id == business_id)\
                  .order_by(Invitation.timestamp.desc()).all()
    finally:
        db.close()
