from app.models.user import User, UserRole

# Estos roles ven todas las sedes. El resto solo ve la suya.
ALL_SITES_ROLES = (UserRole.ADMINISTRADOR, UserRole.GERENTE)


def sees_all_sites(user: User) -> bool:
    return user.role in ALL_SITES_ROLES