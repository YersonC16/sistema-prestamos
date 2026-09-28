import { useState } from "react";
import { useNavigate } from "react-router-dom";
import Card from "@/components/common/Card";
import Input from "@/components/common/Input";
import Button from "@/components/common/Button";
import logo from "@/assets/logo";
import { useAuth } from "@/hooks/useAuth";
import "./Login.css";

function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setIsSubmitting(true);
    try {
      await login({ username: email, password });
      navigate("/inventario");
    } catch {
      setError("Correo o contraseña incorrectos");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="login-page">
      <Card>
        <div className="login-header">
          <img
            src={logo}
            alt="Logo de la organización"
            className="login-logo"
          />
          <h2>Sistema de Préstamos</h2>
          <p className="login-subtitle">Sede Concreto</p>
        </div>

        <form onSubmit={handleSubmit} className="login-form">
          <Input
            label="Correo electrónico"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="usuario@concreto.com"
            required
          />
          <Input
            label="Contraseña"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="••••••••"
            required
          />
          {error && <p className="login-error">{error}</p>}
          <Button type="submit" isLoading={isSubmitting}>
            Iniciar sesión
          </Button>
        </form>
      </Card>
    </div>
  );
}

export default Login;
