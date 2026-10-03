import { Link, Navigate } from "react-router-dom";
import Icon from "@/components/common/Icon";
import type { IconName } from "@/components/common/Icon/Icon";
import logo from "@/assets/logo";
import { useAuth } from "@/hooks/useAuth";
import "./Home.css";

interface FeatureCard {
  icon: IconName;
  title: string;
  description: string;
}

const FEATURES: FeatureCard[] = [
  {
    icon: "package",
    title: "Inventario centralizado",
    description:
      "Equipos y herramientas con código, estado y ubicación, siempre al día.",
  },
  {
    icon: "repeat",
    title: "Préstamos trazables",
    description:
      "Quién tiene cada activo, desde cuándo y hasta cuándo, en un solo lugar.",
  },
  {
    icon: "tool",
    title: "Mantenimiento interno y externo",
    description:
      "Asigna a un técnico propio o a un proveedor, y escala si hace falta.",
  },
  {
    icon: "clock",
    title: "Historial completo",
    description: "Cada movimiento queda registrado: quién, qué y cuándo.",
  },
  {
    icon: "shield",
    title: "Roles y seguridad",
    description: "Accesos diferenciados por rol, con auditoría de cada sesión.",
  },
  {
    icon: "users",
    title: "Responsables",
    description:
      "Personas con documento y contacto, listas para asignar en segundos.",
  },
];

function Home() {
  const { user } = useAuth();

  if (user) {
    return <Navigate to="/panel" replace />;
  }

  return (
    <div className="home-page">
      <header className="home-navbar">
        <div className="home-brand">
          <img src={logo} alt="Logo de la organización" className="home-logo" />
          <div>
            <span className="home-title">Control de préstamos</span>
            <span className="home-subtitle">Sede Concreto</span>
          </div>
        </div>
        <Link to="/login" className="home-login-btn">
          Iniciar sesión
        </Link>
      </header>

      <main className="home-hero">
        <div className="home-hero-badge">
          <Icon name="sparkles" size={14} /> Sistema de gestión de activos
        </div>
        <h1>Control total de tus equipos y herramientas</h1>
        <p>
          Registra, presta, devuelve y da mantenimiento, todo con trazabilidad
          completa y en un solo sistema.
        </p>
        <Link to="/login" className="home-cta">
          Ingresar al sistema <Icon name="arrowRight" size={18} />
        </Link>
      </main>

      <section className="home-features">
        {FEATURES.map((feature) => (
          <div className="feature-card" key={feature.title}>
            <div className="feature-card-inner">
              <div className="feature-icon">
                <Icon name={feature.icon} size={26} />
              </div>
              <h3>{feature.title}</h3>
              <p>{feature.description}</p>
            </div>
          </div>
        ))}
      </section>

      <footer className="home-footer">
        <Icon name="layers" size={16} /> Sistema de Gestión y Control de
        Préstamos — Sede Concreto
      </footer>
    </div>
  );
}

export default Home;
