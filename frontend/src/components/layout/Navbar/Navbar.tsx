import logo from "@/assets/logo";
import { useAuth } from "@/hooks/useAuth";
import "./Navbar.css";

interface NavbarProps {
  onToggleSidebar: () => void;
}

const ROLE_LABELS: Record<string, string> = {
  administrador: "Administrador",
  almacenista: "Almacenista",
  personal_autorizado: "Personal autorizado",
};

function Navbar({ onToggleSidebar }: NavbarProps) {
  const { user, logout } = useAuth();

  return (
    <header className="navbar">
      <button
        className="navbar-toggle"
        onClick={onToggleSidebar}
        aria-label="Abrir menú"
      >
        ☰
      </button>
      <img src={logo} alt="Logo de la organización" className="navbar-logo" />
      <span className="navbar-title">Sistema de Préstamos — Sede Concreto</span>

      {user && (
        <div className="navbar-user">
          <span className="navbar-user-name">
            {user.full_name}{" "}
            <span className="navbar-user-role">({ROLE_LABELS[user.role]})</span>
          </span>
          <button className="navbar-logout" onClick={logout}>
            Cerrar sesión
          </button>
        </div>
      )}
    </header>
  );
}

export default Navbar;
