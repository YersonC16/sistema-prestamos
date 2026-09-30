import logo from "@/assets/logo";
import Icon from "@/components/common/Icon";
import { useAuth } from "@/hooks/useAuth";
import { initials } from "@/utils/format";
import { ROLE_LABEL } from "@/utils/labels";
import "./Navbar.css";

interface NavbarProps {
  onToggleSidebar: () => void;
  onChangePassword: () => void;
}

function Navbar({ onToggleSidebar, onChangePassword }: NavbarProps) {
  const { user, logout } = useAuth();

  return (
    <header className="navbar">
      <button
        className="navbar-icon-btn navbar-toggle"
        onClick={onToggleSidebar}
        aria-label="Abrir menú"
      >
        <Icon name="menu" size={22} />
      </button>
      <img src={logo} alt="Logo de la organización" className="navbar-logo" />
      <div className="navbar-brand">
        <span className="navbar-title">Control de préstamos</span>
        <span className="navbar-subtitle">Sede Concreto</span>
      </div>

      {user && (
        <div className="navbar-user">
          <div className="navbar-avatar" aria-hidden="true">
            {initials(user.full_name)}
          </div>
          <div className="navbar-user-info">
            <span className="navbar-user-name">{user.full_name}</span>
            <span className="navbar-user-role">{ROLE_LABEL[user.role]}</span>
          </div>
          <button
            className="navbar-icon-btn"
            onClick={onChangePassword}
            aria-label="Cambiar contraseña"
            title="Cambiar contraseña"
          >
            <Icon name="key" />
          </button>
          <button
            className="navbar-icon-btn"
            onClick={logout}
            aria-label="Cerrar sesión"
            title="Cerrar sesión"
          >
            <Icon name="logout" />
          </button>
        </div>
      )}
    </header>
  );
}

export default Navbar;
