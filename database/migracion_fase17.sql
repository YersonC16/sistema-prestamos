-- 1) Limpieza: tablas y tipos que las pruebas crearon por error en public
DROP TABLE IF EXISTS public.assets CASCADE;
DROP TABLE IF EXISTS public.users CASCADE;
DROP TABLE IF EXISTS public.loans CASCADE;
DROP TYPE IF EXISTS public.assetstatus CASCADE;
DROP TYPE IF EXISTS public.assettype CASCADE;
DROP TYPE IF EXISTS public.userrole CASCADE;
DROP TYPE IF EXISTS public.loanstatus CASCADE;

-- 2) asset-service: codigo del activo y usuarios activos/inactivos
ALTER TABLE assets.assets ADD COLUMN IF NOT EXISTS code VARCHAR(50);
CREATE UNIQUE INDEX IF NOT EXISTS uq_assets_code ON assets.assets (code);
ALTER TABLE assets.users ADD COLUMN IF NOT EXISTS is_active BOOLEAN NOT NULL DEFAULT TRUE;

-- 3) loan-service: trazabilidad del prestamo
ALTER TABLE loans.loans
  ADD COLUMN IF NOT EXISTS asset_name VARCHAR(150),
  ADD COLUMN IF NOT EXISTS notes VARCHAR(255),
  ADD COLUMN IF NOT EXISTS registered_by_id INTEGER,
  ADD COLUMN IF NOT EXISTS registered_by_name VARCHAR(150),
  ADD COLUMN IF NOT EXISTS returned_by_name VARCHAR(150),
  ADD COLUMN IF NOT EXISTS return_condition VARCHAR(30),
  ADD COLUMN IF NOT EXISTS return_notes VARCHAR(500);