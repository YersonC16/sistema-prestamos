import pytest

from app.models.notification_log import NotificationLog
from app.models.user import UserRole
from app.services.event_consumer import _apply_event
from app.services.notifications.events import DomainEvent
from app.services.notifications.messages import build_message
from app.services.notifications.observers import PlantManagerEmailObserver, SynchronousExecutor
from app.services.notifications.subject import EventSubject, Observer, get_event_subject
from tests.conftest import TestingSessionLocal


def _auth(token):
    return {"Authorization": f"Bearer {token}"}


def _create_asset(client, token, name="Taladro"):
    response = client.post("/assets/", json={"name": name, "asset_type": "herramienta"}, headers=_auth(token))
    assert response.status_code == 200
    return response.json()


@pytest.fixture
def sent(monkeypatch):
    """Conecta el observador REAL a la base de pruebas y guarda cada correo en una lista."""
    monkeypatch.setattr("app.services.notifications.observers.SessionLocal", TestingSessionLocal)
    monkeypatch.setattr("app.services.event_consumer.SessionLocal", TestingSessionLocal)
    messages = []

    def fake_sender(to, subject, body):
        messages.append({"to": to, "subject": subject, "body": body})
        return "correo"

    observer = PlantManagerEmailObserver(sender=fake_sender, executor=SynchronousExecutor())
    get_event_subject().attach(observer)
    yield messages
    get_event_subject().detach(observer)


class Recorder(Observer):
    def __init__(self):
        self.events = []

    def update(self, event):
        self.events.append(event)


class Broken(Observer):
    def update(self, event):
        raise RuntimeError("boom")


# ---------- El patrón Observer ----------

def test_un_observador_que_falla_no_impide_que_los_demas_reciban():
    subject = EventSubject()
    recorder = Recorder()
    subject.attach(Broken())
    subject.attach(recorder)
    subject.notify(DomainEvent(type="prestamo_creado", site="concreto"))
    assert len(recorder.events) == 1


def test_detach_deja_de_avisar_al_observador():
    subject = EventSubject()
    recorder = Recorder()
    subject.attach(recorder)
    subject.detach(recorder)
    subject.notify(DomainEvent(type="prestamo_creado", site="concreto"))
    assert recorder.events == []


def test_el_mensaje_incluye_sede_activo_y_responsable_del_cambio():
    event = DomainEvent(
        type="mantenimiento_finalizado", site="concreto", asset_name="Taladro", actor="Ana", detail="Finalizado por Carlos"
    )
    subject, body = build_message(event)
    assert subject == "[Concreto] Mantenimiento finalizado: Taladro"
    assert "Realizado por: Ana" in body
    assert "Finalizado por Carlos" in body


# ---------- A quién se notifica ----------

def test_el_jefe_de_planta_recibe_correo_al_registrar_un_activo(client, make_user, sent):
    _, admin_token = make_user(UserRole.ADMINISTRADOR)
    make_user(UserRole.JEFE_DE_PLANTA, email="jefe@concreto.com")

    _create_asset(client, admin_token)

    assert len(sent) == 1
    assert sent[0]["to"] == "jefe@concreto.com"
    assert sent[0]["subject"] == "[Concreto] Nuevo activo registrado: Taladro"


def test_no_se_notifica_a_gerente_almacenista_ni_administrador(client, make_user, sent, db_session):
    _, admin_token = make_user(UserRole.ADMINISTRADOR)
    make_user(UserRole.GERENTE)
    make_user(UserRole.ALMACENISTA)

    _create_asset(client, admin_token)

    assert sent == []
    assert [row.status for row in db_session.query(NotificationLog).all()] == ["sin_destinatario"]


def test_solo_recibe_el_jefe_de_la_sede_del_evento(client, make_user, sent, db_session):
    _, admin_token = make_user(UserRole.ADMINISTRADOR)
    make_user(UserRole.JEFE_DE_PLANTA, email="concreto@test.com")
    other, _ = make_user(UserRole.JEFE_DE_PLANTA, email="norte@test.com")
    other.site = "norte"
    db_session.commit()

    _create_asset(client, admin_token)

    assert [message["to"] for message in sent] == ["concreto@test.com"]


def test_un_jefe_de_planta_desactivado_no_recibe(client, make_user, sent):
    _, admin_token = make_user(UserRole.ADMINISTRADOR)
    make_user(UserRole.JEFE_DE_PLANTA, email="baja@test.com", is_active=False)

    _create_asset(client, admin_token)

    assert sent == []


def test_un_solo_jefe_de_planta_activo_por_sede(client, make_user):
    _, admin_token = make_user(UserRole.ADMINISTRADOR)
    body = {"full_name": "Jefe Uno", "email": "uno@test.com", "password": "Clave2026x", "role": "jefe_de_planta"}

    assert client.post("/auth/register", json=body, headers=_auth(admin_token)).status_code == 200

    second = {**body, "full_name": "Jefe Dos", "email": "dos@test.com"}
    assert client.post("/auth/register", json=second, headers=_auth(admin_token)).status_code == 409

    other_site = {**second, "site": "norte"}
    assert client.post("/auth/register", json=other_site, headers=_auth(admin_token)).status_code == 200


# ---------- Qué eventos notifican ----------

def test_un_envio_fallido_se_registra_sin_romper_la_operacion(client, make_user, monkeypatch, db_session):
    monkeypatch.setattr("app.services.notifications.observers.SessionLocal", TestingSessionLocal)

    def failing_sender(to, subject, body):
        raise ConnectionError("SMTP caído")

    observer = PlantManagerEmailObserver(sender=failing_sender, executor=SynchronousExecutor())
    get_event_subject().attach(observer)
    try:
        _, admin_token = make_user(UserRole.ADMINISTRADOR)
        make_user(UserRole.JEFE_DE_PLANTA, email="jefe@concreto.com")
        _create_asset(client, admin_token)  # debe responder 200 aunque el correo falle
    finally:
        get_event_subject().detach(observer)

    row = db_session.query(NotificationLog).one()
    assert row.status == "fallido"
    assert "SMTP caído" in row.error


def test_el_mantenimiento_notifica_al_jefe_de_planta(client, make_user, sent):
    _, admin_token = make_user(UserRole.ADMINISTRADOR)
    make_user(UserRole.JEFE_DE_PLANTA, email="jefe@concreto.com")
    asset = _create_asset(client, admin_token)

    started = client.post(
        "/maintenance/",
        json={
            "asset_id": asset["id"],
            "location": "interno",
            "assigned_to": "Carlos Ruiz",
            "maintenance_type": "correctivo",
            "reason": "Cambio de carbones",
        },
        headers=_auth(admin_token),
    )
    assert started.status_code == 200

    assert len(sent) == 2  # activo registrado + mantenimiento iniciado
    assert "Mantenimiento iniciado" in sent[1]["subject"]
    assert "Carlos Ruiz" in sent[1]["body"]


def test_los_eventos_de_prestamo_llegan_por_el_broker_y_notifican(client, make_user, sent):
    _, admin_token = make_user(UserRole.ADMINISTRADOR)
    make_user(UserRole.JEFE_DE_PLANTA, email="jefe@concreto.com")
    asset = _create_asset(client, admin_token)

    _apply_event(
        "prestamo.creado",
        {
            "asset_id": asset["id"],
            "loan_id": 1,
            "responsible_name": "Juan Pérez",
            "expected_return_date": "2026-12-01T00:00:00",
            "registered_by": "Ana Almacén",
        },
    )
    _apply_event(
        "prestamo.devuelto",
        {
            "asset_id": asset["id"],
            "loan_id": 1,
            "responsible_name": "Juan Pérez",
            "condition": "con_novedad",
            "notes": "Cable pelado",
            "returned_by": "Ana Almacén",
            "maintenance_location": "interno",
            "maintenance_assigned_to": "Carlos Ruiz",
        },
    )

    subjects = [message["subject"] for message in sent]
    assert "[Concreto] Préstamo registrado: Taladro" in subjects
    assert "[Concreto] Devolución con novedad: Taladro" in subjects
    assert client.get(f"/assets/{asset['id']}", headers=_auth(admin_token)).json()["status"] == "mantenimiento"


# ---------- Historial y laboratorio ----------

def test_el_historial_de_notificaciones_depende_del_rol(client, make_user, db_session):
    db_session.add_all(
        [
            NotificationLog(event_type="prestamo_creado", site="concreto", channel="simulado", status="simulado"),
            NotificationLog(event_type="prestamo_creado", site="norte", channel="simulado", status="simulado"),
        ]
    )
    db_session.commit()
    _, admin_token = make_user(UserRole.ADMINISTRADOR)
    _, manager_token = make_user(UserRole.GERENTE)
    _, plant_token = make_user(UserRole.JEFE_DE_PLANTA)
    _, store_token = make_user(UserRole.ALMACENISTA)

    assert len(client.get("/notifications/", headers=_auth(admin_token)).json()) == 2
    assert len(client.get("/notifications/", headers=_auth(manager_token)).json()) == 2  # gerente: todas las sedes

    plant_rows = client.get("/notifications/", headers=_auth(plant_token)).json()
    assert [row["site"] for row in plant_rows] == ["concreto"]  # jefe: solo su sede

    assert client.get("/notifications/", headers=_auth(store_token)).status_code == 403


def test_el_laboratorio_ejecuta_los_cuatro_enfoques(client, make_user, monkeypatch, db_session):
    monkeypatch.setattr("app.services.notifications.observers.SessionLocal", TestingSessionLocal)
    _, admin_token = make_user(UserRole.ADMINISTRADOR, email="lab-admin@test.com")
    make_user(UserRole.JEFE_DE_PLANTA, email="jefe@concreto.com")
    _, store_token = make_user(UserRole.ALMACENISTA, email="lab-store@test.com")
    body = {"event_type": "prestamo_creado", "site": "concreto", "channel": "simulado"}

    response = client.post("/lab/notifications", json=body, headers=_auth(admin_token))
    assert response.status_code == 200

    reports = response.json()["reports"]
    assert [report["mode"] for report in reports] == ["sin_patron", "observer", "strategy", "observer_strategy"]
    for report in reports:
        assert report["steps"]
        assert len(report["deliveries"]) == 1
        assert report["deliveries"][0]["recipient"] == "jefe@concreto.com"
        assert report["deliveries"][0]["status"] == "simulado"

    assert db_session.query(NotificationLog).count() == 4  # cada variante deja su registro
    assert client.post("/lab/notifications", json=body, headers=_auth(store_token)).status_code == 403