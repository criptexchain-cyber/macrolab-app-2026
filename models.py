from datetime import datetime
from typing import Optional
from sqlalchemy import create_engine, String, Float, Integer, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

# 1. Configuración de la Base de Datos
DATABASE_URL = "sqlite:///./dietas.db"
engine = create_engine(DATABASE_URL)

class Base(DeclarativeBase):
    pass

# --- TABLA DE USUARIOS ---
class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    
    profile: Mapped["UserProfile"] = relationship(back_populates="user", uselist=False)

# --- TABLA DE PERFIL FÍSICO ---
class UserProfile(Base):
    __tablename__ = "user_profiles"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    age: Mapped[int] = mapped_column(Integer)
    weight_kg: Mapped[float] = mapped_column(Float)
    height_cm: Mapped[float] = mapped_column(Float)
    gender: Mapped[str] = mapped_column(String(10))
    activity_level: Mapped[float] = mapped_column(Float)
    goal: Mapped[str] = mapped_column(String(20))

    user: Mapped["User"] = relationship(back_populates="profile")

# --- TABLA DE ALIMENTOS (BEDCA) ---
# Esta es la parte que faltaba y causaba tu error
class BedcaFood(Base):
    __tablename__ = "bedca_foods"

    id: Mapped[int] = mapped_column(primary_key=True)
    bedca_id: Mapped[str] = mapped_column(String(20), unique=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    
    # Macros por cada 100g
    calories: Mapped[float] = mapped_column(Float)
    protein: Mapped[float] = mapped_column(Float)
    carbohydrates: Mapped[float] = mapped_column(Float)
    fat: Mapped[float] = mapped_column(Float)
    fiber: Mapped[float] = mapped_column(Float, default=0.0)

# Función para guardar los cambios
def init_db():
    print("🏗️  Construyendo base de datos...")
    Base.metadata.create_all(bind=engine)
    print("✅ Todo listo: Tablas de Usuarios y Alimentos creadas.")

if __name__ == "__main__":
    init_db()