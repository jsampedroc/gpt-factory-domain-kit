-- Audit log: records all CREATE/UPDATE/DELETE actions
CREATE TABLE IF NOT EXISTS audit_log (
    id            UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_type   VARCHAR(64)  NOT NULL,
    entity_id     VARCHAR(64),
    action        VARCHAR(16)  NOT NULL,
    performed_by  VARCHAR(128),
    performed_at  TIMESTAMP    NOT NULL DEFAULT now(),
    details       VARCHAR(2000)
);
CREATE INDEX IF NOT EXISTS idx_audit_entity ON audit_log(entity_type, entity_id);
CREATE INDEX IF NOT EXISTS idx_audit_user ON audit_log(performed_by);

-- Insurance / convenio per patient
CREATE TABLE IF NOT EXISTS insurance (
    id                 UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id         UUID         NOT NULL,
    insurance_company  VARCHAR(128) NOT NULL,
    policy_number      VARCHAR(64),
    coverage_type      VARCHAR(32),
    coverage_percent   INTEGER CHECK (coverage_percent BETWEEN 0 AND 100),
    valid_until        DATE,
    notes              VARCHAR(500)
);
CREATE INDEX IF NOT EXISTS idx_insurance_patient ON insurance(patient_id);
