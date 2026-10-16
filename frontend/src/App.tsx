import { Navigate, Route, Routes } from "react-router-dom";
import AppLayout from "@/components/layout/AppLayout";
import ProtectedRoute from "@/components/layout/ProtectedRoute";
import { AuthProvider } from "@/context/AuthContext";
import AssetDetail from "@/pages/AssetDetail";
import Dashboard from "@/pages/Dashboard";
import Home from "@/pages/Home";
import Inventory from "@/pages/Inventory";
import Loans from "@/pages/Loans";
import Login from "@/pages/Login";
import Maintenance from "@/pages/Maintenance";
import Responsibles from "@/pages/Responsibles";
import Traceability from "@/pages/Traceability";
import Users from "@/pages/Users";

function App() {
  return (
    <AuthProvider>
      <Routes>
        {/* Rutas públicas: fuera de ProtectedRoute */}
        <Route path="/" element={<Home />} />
        <Route path="/login" element={<Login />} />

        {/* Rutas protegidas */}
        <Route
          element={
            <ProtectedRoute>
              <AppLayout />
            </ProtectedRoute>
          }
        >
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
        </Route>

        {/* Cualquier ruta no reconocida vuelve al Home público */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </AuthProvider>
  );
}

export default App;
