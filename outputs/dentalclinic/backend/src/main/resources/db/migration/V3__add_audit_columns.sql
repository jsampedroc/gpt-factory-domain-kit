-- ============================================================
-- V3: Audit columns (created_at, updated_at, created_by, updated_by)
-- ============================================================

ALTER TABLE patient
    ADD COLUMN IF NOT EXISTS created_at  TIMESTAMP,
    ADD COLUMN IF NOT EXISTS updated_at  TIMESTAMP,
    ADD COLUMN IF NOT EXISTS created_by  VARCHAR(100),
    ADD COLUMN IF NOT EXISTS updated_by  VARCHAR(100);

ALTER TABLE dentist
    ADD COLUMN IF NOT EXISTS created_at  TIMESTAMP,
    ADD COLUMN IF NOT EXISTS updated_at  TIMESTAMP,
    ADD COLUMN IF NOT EXISTS created_by  VARCHAR(100),
    ADD COLUMN IF NOT EXISTS updated_by  VARCHAR(100);

ALTER TABLE appointment
    ADD COLUMN IF NOT EXISTS created_at  TIMESTAMP,
    ADD COLUMN IF NOT EXISTS updated_at  TIMESTAMP,
    ADD COLUMN IF NOT EXISTS created_by  VARCHAR(100),
    ADD COLUMN IF NOT EXISTS updated_by  VARCHAR(100);

ALTER TABLE treatment
    ADD COLUMN IF NOT EXISTS created_at  TIMESTAMP,
    ADD COLUMN IF NOT EXISTS updated_at  TIMESTAMP,
    ADD COLUMN IF NOT EXISTS created_by  VARCHAR(100),
    ADD COLUMN IF NOT EXISTS updated_by  VARCHAR(100);

ALTER TABLE invoice
    ADD COLUMN IF NOT EXISTS created_at  TIMESTAMP,
    ADD COLUMN IF NOT EXISTS updated_at  TIMESTAMP,
    ADD COLUMN IF NOT EXISTS created_by  VARCHAR(100),
    ADD COLUMN IF NOT EXISTS updated_by  VARCHAR(100);
