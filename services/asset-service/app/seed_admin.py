"""
Script de un solo uso para crear el primer usuario administrador.
Ejecutar manualmente: python -m app.seed_admin
"""
from app.core.database import SessionLocal, Base, engine
from app.core.security import hash_password
from app.models.user import User, UserRole

Base.metadata.create_all(bind=engine)

def create_first_admin():
    db = SessionLocal()
    existing = db.query(User).filter(User.email == "admin@concreto.com").first()
    if existing:
        print("Ya existe un administrador con ese correo.")
        return

    admin = User(
        full_name="Administrador Sede Concreto",
        email="admin@concreto.com",
        hashed_password=hash_password("Admin123!"),
        role=UserRole.ADMINISTRADOR,
    )
    db.add(admin)
    db.commit()
    print("Administrador creado: admin@concreto.com / Admin123!")
    db.close()

if __name__ == "__main__":
    create_first_admin()