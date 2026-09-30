import { useState, type FormEvent } from "react";
import { Navigate, useNavigate } from "react-router-dom";
import Alert from "@/components/common/Alert";
import Button from "@/components/common/Button";
import Card from "@/components/common/Card";
import Input from "@/components/common/Input";
import logo from "@/assets/logo";
import { useAuth } from "@/hooks/useAuth";
import { getErrorMessage } from "@/utils/errors";
import "./Login.css";

function Login() {
  const { user, login } = useAuth();
  const navigate = useNavigate();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  if (user) {
    return <Navigate to="/panel" replace />;
  }

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setError("");
    setIsSubmitting(true);
    try {
      await login({ username: email.trim(), password });
      navigate("/panel");
    } catch (err) {
      setError(getErrorMessage(err, "No se pudo iniciar sesión"));
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
          <h2>Control de préstamos</h2>
          <p className="login-subtitle">Sede Concreto</p>
        </div>

        <form onSubmit={handleSubmit} className="login-form">
          <Input
            label="Correo electrónico"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="usuario@concreto.com"
            autoComplete="username"
            required
          />
          <Input
            label="Contraseña"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="••••••••"
            autoComplete="current-password"
            required
          />
          {error && <Alert>{error}</Alert>}
          <Button type="submit" isLoading={isSubmitting}>
            Iniciar sesión
          </Button>
        </form>
      </Card>
    </div>
  );
}

export default Login;
