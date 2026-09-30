import { useState } from "react";
import { Outlet } from "react-router-dom";
import ChangePasswordModal from "./ChangePasswordModal";
import Navbar from "./Navbar";
import Sidebar from "./Sidebar";
import "./AppLayout.css";

function AppLayout() {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [isPasswordOpen, setIsPasswordOpen] = useState(false);

  return (
    <div className="app-layout">
      <Navbar
        onToggleSidebar={() => setIsSidebarOpen((prev) => !prev)}
        onChangePassword={() => setIsPasswordOpen(true)}
      />
      <div className="app-body">
        <Sidebar
          isOpen={isSidebarOpen}
          onClose={() => setIsSidebarOpen(false)}
        />
        <main className="app-content">
          <Outlet />
        </main>
      </div>
      <ChangePasswordModal
        isOpen={isPasswordOpen}
        onClose={() => setIsPasswordOpen(false)}
      />
    </div>
  );
}

export default AppLayout;
