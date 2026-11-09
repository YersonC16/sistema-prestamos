-- Nuevo estado del activo
ALTER TYPE assets.assetstatus ADD VALUE IF NOT EXISTS 'baja';

-- Marca, numero de serie y datos de la baja
ALTER TABLE assets.assets
  ADD COLUMN IF NOT EXISTS brand VARCHAR(100),
  ADD COLUMN IF NOT EXISTS serial_number VARCHAR(100),
  ADD COLUMN IF NOT EXISTS decommissioned_at TIMESTAMPTZ,
  ADD COLUMN IF NOT EXISTS decommission_reason VARCHAR(500),
  ADD COLUMN IF NOT EXISTS decommissioned_by VARCHAR(150);