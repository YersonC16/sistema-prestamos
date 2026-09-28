import { NavLink } from "react-router-dom";
import "./Sidebar.css";

interface SidebarProps {
  isOpen: boolean;
  onClose: () => void;
}

function Sidebar({ isOpen, onClose }: SidebarProps) {
  return (
    <>
      {isOpen && <div className="sidebar-overlay" onClick={onClose} />}
      <aside className={`sidebar ${isOpen ? "sidebar-open" : ""}`}>
        <NavLink to="/inventario" className="sidebar-link" onClick={onClose}>
          Inventario
        </NavLink>
        <NavLink to="/prestamos" className="sidebar-link" onClick={onClose}>
          Préstamos
        </NavLink>
      </aside>
    </>
  );
}

export default Sidebar;
