import { useCallback, useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import Icon from "@/components/common/Icon";
import { inboxService } from "@/services/inboxService";
import type { InboxItem, InboxResponse } from "@/types/inbox";
import { timeAgo } from "@/utils/format";
import { actionMeta } from "@/utils/labels";
import "./NotificationBell.css";

const POLL_MS = 30_000;

function NotificationBell() {
  const navigate = useNavigate();
  const containerRef = useRef<HTMLDivElement>(null);
  const lastCount = useRef(0);

  const [open, setOpen] = useState(false);
  const [data, setData] = useState<InboxResponse>({
    unread_count: 0,
    items: [],
  });
  const [hasError, setHasError] = useState(false);
  const [ringing, setRinging] = useState(false);

  const refresh = useCallback(async () => {
    try {
      const next = await inboxService.get();
      if (next.unread_count > lastCount.current) {
        setRinging(true);
        window.setTimeout(() => setRinging(false), 1200);
      }
      lastCount.current = next.unread_count;
      setData(next);
      setHasError(false);
    } catch {
      setHasError(true);
    }
  }, []);

  // Pregunta al iniciar, cada 30 segundos y al volver a la pestaña
  useEffect(() => {
    void refresh();
    const timer = window.setInterval(() => void refresh(), POLL_MS);
    const onFocus = () => void refresh();
    window.addEventListener("focus", onFocus);
    return () => {
      window.clearInterval(timer);
      window.removeEventListener("focus", onFocus);
    };
  }, [refresh]);

  // Cierra el panel al hacer clic afuera o con Escape
  useEffect(() => {
    if (!open) return;
    const onMouseDown = (event: MouseEvent) => {
      if (
        containerRef.current &&
        !containerRef.current.contains(event.target as Node)
      )
        setOpen(false);
    };
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") setOpen(false);
    };
    document.addEventListener("mousedown", onMouseDown);
    document.addEventListener("keydown", onKeyDown);
    return () => {
      document.removeEventListener("mousedown", onMouseDown);
      document.removeEventListener("keydown", onKeyDown);
    };
  }, [open]);

  const toggle = () => {
    if (!open) void refresh();
    setOpen((previous) => !previous);
  };

  const openItem = (item: InboxItem) => {
    setOpen(false);
    if (item.asset_id) navigate(`/inventario/${item.asset_id}`);
    if (!item.is_read) {
      void inboxService
        .markRead(item.id)
        .then(refresh)
        .catch(() => undefined);
    }
  };

  const markAll = async () => {
    try {
      await inboxService.markAllRead();
      await refresh();
    } catch {
      setHasError(true);
    }
  };

  const unread = data.unread_count;

  return (
    <div className="bell" ref={containerRef}>
      <button
        className={`navbar-icon-btn bell-button ${ringing ? "bell-ring" : ""}`}
        onClick={toggle}
        aria-label={`Notificaciones, ${unread} sin leer`}
        aria-expanded={open}
        title="Notificaciones"
      >
        <Icon name="bell" size={20} />
        {unread > 0 && (
          <span className="bell-badge">{unread > 9 ? "9+" : unread}</span>
        )}
      </button>

      {open && (
        <div className="bell-panel" role="dialog" aria-label="Notificaciones">
          <div className="bell-panel-header">
            <strong>Notificaciones</strong>
            {unread > 0 && (
              <button className="bell-link" onClick={markAll}>
                Marcar todas como leídas
              </button>
            )}
          </div>

          {hasError && (
            <p className="bell-empty">
              No se pudo cargar. Se reintentará en unos segundos.
            </p>
          )}
          {!hasError && data.items.length === 0 && (
            <p className="bell-empty">No tienes notificaciones</p>
          )}

          <ul className="bell-list">
            {data.items.map((item) => (
              <li key={item.id}>
                <button
                  className={`bell-item ${item.is_read ? "" : "bell-item-unread"}`}
                  onClick={() => openItem(item)}
                >
                  <span
                    className={`bell-dot bell-dot-${actionMeta(item.event_type).tone}`}
                  />
                  <span className="bell-item-body">
                    <span className="bell-item-title">{item.title}</span>
                    <span className="bell-item-message">{item.message}</span>
                    <span className="bell-item-time">
                      {timeAgo(item.created_at)}
                    </span>
                  </span>
                </button>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

export default NotificationBell;
