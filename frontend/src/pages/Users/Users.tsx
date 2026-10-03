import { useCallback, useState, type FormEvent } from "react";
import Alert from "@/components/common/Alert";
import Badge from "@/components/common/Badge";
import Button from "@/components/common/Button";
import Card from "@/components/common/Card";
import Icon from "@/components/common/Icon";
import Input from "@/components/common/Input";
import Modal from "@/components/common/Modal";
import PageHeader from "@/components/common/PageHeader";
import Pagination from "@/components/common/Pagination";
import Select from "@/components/common/Select";
import { SkeletonTable } from "@/components/common/Skeleton";
import Table from "@/components/common/Table";
import type { TableColumn } from "@/components/common/Table";
import { useAuth } from "@/hooks/useAuth";
import { useFetch } from "@/hooks/useFetch";
import { usePagination } from "@/hooks/usePagination";
import { userService } from "@/services/userService";
import type { User, UserRole } from "@/types/auth";
import { getErrorMessage } from "@/utils/errors";
import { ROLE_LABEL } from "@/utils/labels";
import { PASSWORD_HINT, validatePassword } from "@/utils/validation";

const ROLES: UserRole[] = [
  "administrador",
  "almacenista",
  "personal_autorizado",
];

function Users() {
  const { user: me } = useAuth();
  const fetchUsers = useCallback(() => userService.getAll(), []);
  const {
    data: users,
    isLoading,
    error,
    refetch,
  } = useFetch<User[]>(fetchUsers);

  const { page, setPage, totalPages, pageItems, total } = usePagination(
    users ?? [],
    10,
  );

  const [isSaving, setIsSaving] = useState(false);

  // Crear
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [newName, setNewName] = useState("");
  const [newEmail, setNewEmail] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [newRole, setNewRole] = useState<UserRole>("personal_autorizado");
  const [createError, setCreateError] = useState("");

  // Editar
  const [editing, setEditing] = useState<User | null>(null);
  const [editName, setEditName] = useState("");
  const [editRole, setEditRole] = useState<UserRole>("personal_autorizado");
  const [editActive, setEditActive] = useState("true");
  const [editError, setEditError] = useState("");

  // Restablecer contraseña
  const [resetTarget, setResetTarget] = useState<User | null>(null);
  const [resetPassword, setResetPassword] = useState("");
  const [resetError, setResetError] = useState("");

  const closeCreate = () => {
    setIsCreateOpen(false);
    setNewName("");
    setNewEmail("");
    setNewPassword("");
    setNewRole("personal_autorizado");
    setCreateError("");
  };

  const handleCreate = async (event: FormEvent) => {
    event.preventDefault();
    if (newName.trim().length < 2)
      return setCreateError("El nombre debe tener al menos 2 caracteres");
    const passwordError = validatePassword(newPassword);
    if (passwordError) return setCreateError(passwordError);

    setIsSaving(true);
    setCreateError("");
    try {
      await userService.create({
        full_name: newName.trim(),
        email: newEmail.trim(),
        password: newPassword,
        role: newRole,
      });
      closeCreate();
      refetch();
    } catch (err) {
      setCreateError(getErrorMessage(err, "No se pudo crear el usuario"));
    } finally {
      setIsSaving(false);
    }
  };

  const openEdit = (target: User) => {
    setEditing(target);
    setEditName(target.full_name);
    setEditRole(target.role);
    setEditActive(String(target.is_active));
    setEditError("");
  };

  const handleEdit = async (event: FormEvent) => {
    event.preventDefault();
    if (!editing) return;
    if (editName.trim().length < 2)
      return setEditError("El nombre debe tener al menos 2 caracteres");

    setIsSaving(true);
    setEditError("");
    try {
      await userService.update(editing.id, {
        full_name: editName.trim(),
        role: editRole,
        is_active: editActive === "true",
      });
      setEditing(null);
      refetch();
    } catch (err) {
      setEditError(getErrorMessage(err, "No se pudo actualizar el usuario"));
    } finally {
      setIsSaving(false);
    }
  };

  const closeReset = () => {
    setResetTarget(null);
    setResetPassword("");
    setResetError("");
  };

  const handleReset = async (event: FormEvent) => {
    event.preventDefault();
    if (!resetTarget) return;
    const passwordError = validatePassword(resetPassword);
    if (passwordError) return setResetError(passwordError);

    setIsSaving(true);
    setResetError("");
    try {
      await userService.resetPassword(resetTarget.id, resetPassword);
      closeReset();
    } catch (err) {
      setResetError(
        getErrorMessage(err, "No se pudo restablecer la contraseña"),
      );
    } finally {
      setIsSaving(false);
    }
  };

  const columns: TableColumn<User>[] = [
    {
      key: "full_name",
      label: "Nombre",
      render: (u) => <span className="cell-strong">{u.full_name}</span>,
    },
    { key: "email", label: "Correo" },
    {
      key: "role",
      label: "Rol",
      render: (u) => <Badge tone="info">{ROLE_LABEL[u.role]}</Badge>,
    },
    {
      key: "is_active",
      label: "Estado",
      render: (u) => (
        <Badge tone={u.is_active ? "success" : "neutral"}>
          {u.is_active ? "Activo" : "Desactivado"}
        </Badge>
      ),
    },
    {
      key: "actions",
      label: "Acciones",
      render: (u) => (
        <div className="cell-actions">
          <Button size="sm" variant="secondary" onClick={() => openEdit(u)}>
            Editar
          </Button>
          <Button size="sm" variant="ghost" onClick={() => setResetTarget(u)}>
            Contraseña
          </Button>
        </div>
      ),
    },
  ];

  const editingSelf = editing !== null && editing.id === me?.id;

  return (
    <div className="page">
      <PageHeader
        title="Usuarios"
        subtitle="Gestión de accesos y roles del sistema."
        actions={
          <Button onClick={() => setIsCreateOpen(true)}>
            <Icon name="plus" size={16} /> Nuevo usuario
          </Button>
        }
      />

      <Card>
        {isLoading && <SkeletonTable rows={4} columns={5} />}
        {error && <Alert>{error}</Alert>}
        {!isLoading && !error && (
          <>
            <Table<User>
              columns={columns}
              data={pageItems}
              keyExtractor={(u) => u.id}
              emptyMessage="No hay usuarios registrados"
            />
            <Pagination
              page={page}
              totalPages={totalPages}
              total={total}
              pageSize={10}
              onChange={setPage}
            />
          </>
        )}
      </Card>

      <Modal isOpen={isCreateOpen} onClose={closeCreate} title="Nuevo usuario">
        <form className="form-stack" onSubmit={handleCreate}>
          <Input
            label="Nombre completo"
            value={newName}
            onChange={(e) => setNewName(e.target.value)}
            required
          />
          <Input
            label="Correo electrónico"
            type="email"
            value={newEmail}
            onChange={(e) => setNewEmail(e.target.value)}
            required
          />
          <Input
            label="Contraseña inicial"
            type="password"
            value={newPassword}
            onChange={(e) => setNewPassword(e.target.value)}
            hint={PASSWORD_HINT}
            autoComplete="new-password"
            required
          />
          <Select
            label="Rol"
            value={newRole}
            onChange={(e) => setNewRole(e.target.value as UserRole)}
          >
            {ROLES.map((role) => (
              <option key={role} value={role}>
                {ROLE_LABEL[role]}
              </option>
            ))}
          </Select>
          {createError && <Alert>{createError}</Alert>}
          <div className="form-actions">
            <Button variant="secondary" onClick={closeCreate}>
              Cancelar
            </Button>
            <Button type="submit" isLoading={isSaving}>
              Crear usuario
            </Button>
          </div>
        </form>
      </Modal>

      <Modal
        isOpen={editing !== null}
        onClose={() => setEditing(null)}
        title="Editar usuario"
      >
        {editing && (
          <form className="form-stack" onSubmit={handleEdit}>
            <p className="muted">{editing.email}</p>
            <Input
              label="Nombre completo"
              value={editName}
              onChange={(e) => setEditName(e.target.value)}
              required
            />
            <Select
              label="Rol"
              value={editRole}
              onChange={(e) => setEditRole(e.target.value as UserRole)}
              disabled={editingSelf}
            >
              {ROLES.map((role) => (
                <option key={role} value={role}>
                  {ROLE_LABEL[role]}
                </option>
              ))}
            </Select>
            <Select
              label="Estado"
              value={editActive}
              onChange={(e) => setEditActive(e.target.value)}
              disabled={editingSelf}
            >
              <option value="true">Activo</option>
              <option value="false">Desactivado</option>
            </Select>
            {editingSelf && (
              <Alert tone="info">
                No puedes cambiar tu propio rol ni desactivar tu cuenta.
              </Alert>
            )}
            {editError && <Alert>{editError}</Alert>}
            <div className="form-actions">
              <Button variant="secondary" onClick={() => setEditing(null)}>
                Cancelar
              </Button>
              <Button type="submit" isLoading={isSaving}>
                Guardar cambios
              </Button>
            </div>
          </form>
        )}
      </Modal>

      <Modal
        isOpen={resetTarget !== null}
        onClose={closeReset}
        title="Restablecer contraseña"
      >
        {resetTarget && (
          <form className="form-stack" onSubmit={handleReset}>
            <p>
              Nueva contraseña para <strong>{resetTarget.full_name}</strong>.
            </p>
            <Input
              label="Nueva contraseña"
              type="password"
              value={resetPassword}
              onChange={(e) => setResetPassword(e.target.value)}
              hint={PASSWORD_HINT}
              autoComplete="new-password"
              required
            />
            {resetError && <Alert>{resetError}</Alert>}
            <div className="form-actions">
              <Button variant="secondary" onClick={closeReset}>
                Cancelar
              </Button>
              <Button type="submit" isLoading={isSaving}>
                Restablecer
              </Button>
            </div>
          </form>
        )}
      </Modal>
    </div>
  );
}

export default Users;
