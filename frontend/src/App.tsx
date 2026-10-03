import { Navigate, Route, Routes } from "react-router-dom";
import AppLayout from "@/components/layout/AppLayout";
import ProtectedRoute from "@/components/layout/ProtectedRoute";
import { AuthProvider } from "@/context/AuthContext";
import AssetDetail from "@/pages/AssetDetail";
import Dashboard from "@/pages/Dashboard";
import Inventory from "@/pages/Inventory";
import Loans from "@/pages/Loans";
import Login from "@/pages/Login";
import Maintenance from "@/pages/Maintenance";
import Traceability from "@/pages/Traceability";
import Users from "@/pages/Users";
import Responsibles from "@/pages/Responsibles";
import Home from "@/pages/Home";

function App() {
  return (
    <AuthProvider>
      <Routes>
        <Route path="/login" element={<Login />} />

        <Route
          element={
            <ProtectedRoute>
              <AppLayout />
            </ProtectedRoute>
          }
        >
          <Route path="/" element={<Home />} />

          <Route path="/panel" element={<Dashboard />} />
          <Route path="/inventario" element={<Inventory />} />
          <Route path="/inventario/:id" element={<AssetDetail />} />
          <Route path="/prestamos" element={<Loans />} />
          <Route path="/mantenimiento" element={<Maintenance />} />
          <Route
            path="/trazabilidad"
            element={
              <ProtectedRoute allowedRoles={["administrador", "almacenista"]}>
                <Traceability />
              </ProtectedRoute>
            }
          />
          <Route
            path="/usuarios"
            element={
              <ProtectedRoute allowedRoles={["administrador"]}>
                <Users />
              </ProtectedRoute>
            }
          />
          <Route
            path="/responsables"
            element={
              <ProtectedRoute allowedRoles={["administrador", "almacenista"]}>
                <Responsibles />
              </ProtectedRoute>
            }
          />
          <Route path="*" element={<Navigate to="/panel" replace />} />
        </Route>
      </Routes>
    </AuthProvider>
  );
}

export default App;
