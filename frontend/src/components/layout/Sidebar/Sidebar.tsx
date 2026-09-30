import { NavLink } from "react-router-dom";
import Icon from "@/components/common/Icon";
import type { IconName } from "@/components/common/Icon/Icon";
import { useAuth } from "@/hooks/useAuth";
import type { UserRole } from "@/types/auth";
import "./Sidebar.css";

interface NavItem {
  to: string;
  label: string;
  icon: IconName;
  roles?: UserRole[];
}

const NAV_ITEMS: NavItem[] = [
  { to: "/panel", label: "Panel", icon: "dashboard" },
  { to: "/inventario", label: "Inventario", icon: "package" },
  { to: "/prestamos", label: "Préstamos", icon: "repeat" },
  { to: "/mantenimiento", label: "Mantenimiento", icon: "tool" },
  {
    to: "/trazabilidad",
    label: "Trazabilidad",
    icon: "clock",
    roles: ["administrador", "almacenista"],
  },
  {
    to: "/usuarios",
    label: "Usuarios",
    icon: "users",
    roles: ["administrador"],
  },
];

interface SidebarProps {
  isOpen: boolean;
  onClose: () => void;
}

function Sidebar({ isOpen, onClose }: SidebarProps) {
  const { user } = useAuth();
  const items = NAV_ITEMS.filter(
    (item) => !item.roles || (user !== null && item.roles.includes(user.role)),
  );

  return (
    <>
      {isOpen && <div className="sidebar-overlay" onClick={onClose} />}
      <aside className={`sidebar ${isOpen ? "sidebar-open" : ""}`}>
        {items.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className="sidebar-link"
            onClick={onClose}
          >
            <Icon name={item.icon} />
            {item.label}
          </NavLink>
        ))}
      </aside>
    </>
  );
}

export default Sidebar;
