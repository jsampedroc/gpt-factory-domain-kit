-- ============================================================
-- V7: Spring Modulith schema - módulos de dominio con prefijos
-- ============================================================

-- SHARED: outbox + audit
CREATE TABLE IF NOT EXISTS outbox_event (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    aggregate_type VARCHAR(100) NOT NULL,
    aggregate_id VARCHAR(100) NOT NULL,
    event_type VARCHAR(200) NOT NULL,
    payload TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    published BOOLEAN NOT NULL DEFAULT FALSE,
    published_at TIMESTAMPTZ
);
CREATE INDEX IF NOT EXISTS idx_outbox_unpublished ON outbox_event(published, created_at) WHERE published = FALSE;

CREATE TABLE IF NOT EXISTS audit_event_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    clinic_id UUID NOT NULL,
    user_id VARCHAR(200),
    action VARCHAR(100) NOT NULL,
    entity_type VARCHAR(100),
    entity_id VARCHAR(100),
    detail TEXT,
    ip_address VARCHAR(50),
    occurred_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_audit_clinic ON audit_event_log(clinic_id, occurred_at DESC);
CREATE INDEX IF NOT EXISTS idx_audit_entity ON audit_event_log(entity_type, entity_id);

-- PATIENT MODULE
CREATE TABLE IF NOT EXISTS core_patient (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    clinic_id UUID NOT NULL,
    full_name VARCHAR(200) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    birth_date DATE,
    dni_nie VARCHAR(20),
    email VARCHAR(200),
    phone VARCHAR(30),
    gender VARCHAR(20),
    blood_type VARCHAR(10),
    address TEXT,
    city VARCHAR(100),
    postal_code VARCHAR(10),
    notes TEXT,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    deleted BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    version BIGINT NOT NULL DEFAULT 0
);
CREATE INDEX IF NOT EXISTS idx_core_patient_clinic ON core_patient(clinic_id) WHERE deleted = FALSE;
CREATE INDEX IF NOT EXISTS idx_core_patient_email ON core_patient(email) WHERE deleted = FALSE;

CREATE TABLE IF NOT EXISTS core_patient_alert (
    patient_id UUID NOT NULL REFERENCES core_patient(id) ON DELETE CASCADE,
    alert_text VARCHAR(500) NOT NULL
);

-- SCHEDULING MODULE
CREATE TABLE IF NOT EXISTS sched_appointment (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    clinic_id UUID NOT NULL,
    patient_id UUID NOT NULL,
    patient_name VARCHAR(200),
    practitioner_id UUID,
    practitioner_name VARCHAR(200),
    chair_id VARCHAR(50),
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL,
    procedure_name VARCHAR(200),
    status VARCHAR(30) NOT NULL DEFAULT 'BOOKED',
    notes TEXT,
    reminder_sent BOOLEAN NOT NULL DEFAULT FALSE,
    deleted BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    version BIGINT NOT NULL DEFAULT 0
);
CREATE INDEX IF NOT EXISTS idx_sched_appt_clinic_date ON sched_appointment(clinic_id, start_time) WHERE deleted = FALSE;
CREATE INDEX IF NOT EXISTS idx_sched_appt_patient ON sched_appointment(patient_id) WHERE deleted = FALSE;

-- CLINICAL MODULE
CREATE TABLE IF NOT EXISTS clin_encounter (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    clinic_id UUID NOT NULL,
    patient_id UUID NOT NULL,
    appointment_id UUID,
    practitioner_id UUID,
    practitioner_name VARCHAR(200),
    encounter_date DATE NOT NULL,
    chief_complaint TEXT,
    clinical_notes TEXT,
    diagnosis TEXT,
    status VARCHAR(30) NOT NULL DEFAULT 'OPEN',
    signed_at TIMESTAMPTZ,
    deleted BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    version BIGINT NOT NULL DEFAULT 0
);
CREATE INDEX IF NOT EXISTS idx_clin_encounter_patient ON clin_encounter(patient_id) WHERE deleted = FALSE;
CREATE INDEX IF NOT EXISTS idx_clin_encounter_clinic ON clin_encounter(clinic_id, encounter_date DESC) WHERE deleted = FALSE;

-- TREATMENT MODULE
CREATE TABLE IF NOT EXISTS treat_plan (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    clinic_id UUID NOT NULL,
    patient_id UUID NOT NULL,
    patient_name VARCHAR(200),
    practitioner_id UUID,
    title VARCHAR(300) NOT NULL,
    description TEXT,
    total_amount NUMERIC(10,2) NOT NULL DEFAULT 0,
    status VARCHAR(30) NOT NULL DEFAULT 'DRAFT',
    accepted_date DATE,
    deleted BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    version BIGINT NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS treat_plan_item (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    plan_id UUID NOT NULL REFERENCES treat_plan(id) ON DELETE CASCADE,
    procedure_code VARCHAR(50),
    procedure_name VARCHAR(300) NOT NULL,
    tooth_number VARCHAR(20),
    quantity INT NOT NULL DEFAULT 1,
    unit_price NUMERIC(10,2) NOT NULL DEFAULT 0,
    discount_percent NUMERIC(5,2) NOT NULL DEFAULT 0,
    status VARCHAR(30) NOT NULL DEFAULT 'PENDING'
);

-- BILLING MODULE
CREATE TABLE IF NOT EXISTS bill_invoice (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    clinic_id UUID NOT NULL,
    invoice_number VARCHAR(50) NOT NULL,
    patient_id UUID NOT NULL,
    patient_name VARCHAR(200),
    issue_date DATE NOT NULL,
    due_date DATE,
    subtotal NUMERIC(10,2) NOT NULL DEFAULT 0,
    tax_percent NUMERIC(5,2) NOT NULL DEFAULT 0,
    tax_amount NUMERIC(10,2) NOT NULL DEFAULT 0,
    total NUMERIC(10,2) NOT NULL DEFAULT 0,
    paid_amount NUMERIC(10,2) NOT NULL DEFAULT 0,
    status VARCHAR(30) NOT NULL DEFAULT 'DRAFT',
    notes TEXT,
    deleted BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    version BIGINT NOT NULL DEFAULT 0,
    UNIQUE(clinic_id, invoice_number)
);
CREATE INDEX IF NOT EXISTS idx_bill_invoice_patient ON bill_invoice(patient_id) WHERE deleted = FALSE;
CREATE INDEX IF NOT EXISTS idx_bill_invoice_clinic ON bill_invoice(clinic_id, issue_date DESC) WHERE deleted = FALSE;

CREATE TABLE IF NOT EXISTS bill_invoice_line (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    invoice_id UUID NOT NULL REFERENCES bill_invoice(id) ON DELETE CASCADE,
    description VARCHAR(500) NOT NULL,
    quantity INT NOT NULL DEFAULT 1,
    unit_price NUMERIC(10,2) NOT NULL,
    discount_percent NUMERIC(5,2) NOT NULL DEFAULT 0,
    total NUMERIC(10,2) NOT NULL
);

CREATE TABLE IF NOT EXISTS bill_payment (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    clinic_id UUID NOT NULL,
    invoice_id UUID NOT NULL REFERENCES bill_invoice(id),
    patient_id UUID NOT NULL,
    amount NUMERIC(10,2) NOT NULL,
    method VARCHAR(30) NOT NULL DEFAULT 'CASH',
    reference VARCHAR(200),
    paid_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_bill_payment_invoice ON bill_payment(invoice_id);
