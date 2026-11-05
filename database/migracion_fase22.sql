-- 1) Renombrar el rol personal_autorizado a gerente (conserva a los usuarios que ya lo tenian)
DO $$
BEGIN
  IF EXISTS (
    SELECT 1 FROM pg_enum e
    JOIN pg_type t ON t.oid = e.enumtypid
    JOIN pg_namespace n ON n.oid = t.typnamespace
    WHERE n.nspname = 'assets' AND t.typname = 'userrole' AND e.enumlabel = 'personal_autorizado'
  ) THEN
    ALTER TYPE assets.userrole RENAME VALUE 'personal_autorizado' TO 'gerente';
  END IF;
END $$;

-- 2) Nuevo rol (va fuera del bloque anterior a proposito)
ALTER TYPE assets.userrole ADD VALUE IF NOT EXISTS 'jefe_de_planta';

-- 3) Sede de cada usuario
ALTER TABLE assets.users ADD COLUMN IF NOT EXISTS site VARCHAR(50) NOT NULL DEFAULT 'concreto';