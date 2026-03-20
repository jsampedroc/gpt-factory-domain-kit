-- Treatment plans and itemized budget
CREATE TABLE IF NOT EXISTS treatment_plans (
    id            UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id    UUID         NOT NULL,
    dentist_id    UUID,
    status        VARCHAR(20)  NOT NULL DEFAULT 'DRAFT',
    total_amount  DECIMAL(10,2) DEFAULT 0,
    created_at    DATE         NOT NULL DEFAULT CURRENT_DATE,
    expires_at    DATE,
    notes         VARCHAR(1000)
);
CREATE INDEX IF NOT EXISTS idx_tp_patient ON treatment_plans(patient_id);
CREATE INDEX IF NOT EXISTS idx_tp_status ON treatment_plans(status);

CREATE TABLE IF NOT EXISTS treatment_plan_items (
    id                UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
    plan_id           UUID         NOT NULL REFERENCES treatment_plans(id) ON DELETE CASCADE,
    tooth_number      INTEGER,
    procedure_code    VARCHAR(32)  NOT NULL,
    description       VARCHAR(255) NOT NULL,
    quantity          INTEGER      NOT NULL DEFAULT 1,
    unit_price        DECIMAL(10,2) NOT NULL,
    total_price       DECIMAL(10,2) NOT NULL,
    insurance_coverage DECIMAL(10,2) DEFAULT 0,
    status            VARCHAR(16)  NOT NULL DEFAULT 'PENDING'
);
CREATE INDEX IF NOT EXISTS idx_tpi_plan ON treatment_plan_items(plan_id);
