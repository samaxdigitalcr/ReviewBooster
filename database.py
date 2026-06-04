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
# 2. MODELS (ACTUALIZADOS PARA MULTI-TENANT)
# ==========================================

class Business(Base):
    __tablename__ = "businesses"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)          # Ej: "Samax Digital" o "Pizzería X"
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False) # Para el futuro Login
    is_active = Column(Boolean, default=True)      # Por si cancelan la suscripción
    
    # Credenciales personalizadas de Twilio para cuando compren su propio número
    twilio_account_sid = Column(String, nullable=True)
    twilio_auth_token = Column(String, nullable=True)
    twilio_whatsapp_number = Column(String, nullable=True)
    
    # Relación con sus invitaciones
    invitations = relationship("Invitation", back_populates="business")


class Invitation(Base):
    __tablename__ = "invitations"
    
    id = Column(Integer, primary_key=True, index=True)
    # Cambio clave: Ahora es una Llave Foránea real apuntando a la tabla de negocios
    business_id = Column(Integer, ForeignKey("businesses.id"), nullable=False)
    customer_name = Column(String, nullable=False)
    customer_phone = Column(String, nullable=False)
    review_url = Column(String)
    status = Column(String, nullable=False)
    twilio_sid = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    is_sinpe = Column(Boolean, default=False)
    
    business = relationship("Business", back_populates="invitations")

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

def get_all_invitations(db, business_id: int):
    """Recupera todas las invitaciones de un negocio específico."""
    return db.query(Invitation).filter(Invitation.business_id == business_id)\
              .order_by(Invitation.timestamp.desc()).all()

def log_invitation(db, business_id, name, phone, url, status, is_sinpe, sid):
    """Registra la invitación usando la sesión activa de FastAPI."""
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
    db.refresh(new_invite)
    return new_invite

