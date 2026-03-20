package com.dentalclinic.clinical.domain;

import com.dentalclinic.shared.kernel.BaseEntity;
import jakarta.persistence.*;
import java.time.LocalDate;
import java.util.UUID;

@Entity
@Table(name = "clin_encounter")
public class Encounter extends BaseEntity {

    @Column(name = "patient_id", nullable = false, columnDefinition = "uuid")
    private UUID patientId;

    @Column(name = "appointment_id", columnDefinition = "uuid")
    private UUID appointmentId;

    @Column(name = "practitioner_id", columnDefinition = "uuid")
    private UUID practitionerId;

    @Column(name = "practitioner_name")
    private String practitionerName;

    @Column(name = "encounter_date", nullable = false)
    private LocalDate encounterDate;

    @Column(name = "chief_complaint", columnDefinition = "text")
    private String chiefComplaint;

    @Column(name = "clinical_notes", columnDefinition = "text")
    private String clinicalNotes;

    @Column(name = "diagnosis", columnDefinition = "text")
    private String diagnosis;

    @Column(name = "status", nullable = false)
    @Enumerated(EnumType.STRING)
    private EncounterStatus status = EncounterStatus.OPEN;

    @Column(name = "signed_at")
    private java.time.Instant signedAt;

    protected Encounter() {}

    public Encounter(UUID patientId, UUID practitionerId, String practitionerName,
                     LocalDate encounterDate, UUID clinicId) {
        this.patientId = patientId;
        this.practitionerId = practitionerId;
        this.practitionerName = practitionerName;
        this.encounterDate = encounterDate;
        setClinicId(clinicId);
    }

    public UUID getPatientId() { return patientId; }
    public UUID getAppointmentId() { return appointmentId; }
    public void setAppointmentId(UUID appointmentId) { this.appointmentId = appointmentId; }
    public UUID getPractitionerId() { return practitionerId; }
    public String getPractitionerName() { return practitionerName; }
    public LocalDate getEncounterDate() { return encounterDate; }
    public String getChiefComplaint() { return chiefComplaint; }
    public void setChiefComplaint(String chiefComplaint) { this.chiefComplaint = chiefComplaint; }
    public String getClinicalNotes() { return clinicalNotes; }
    public void setClinicalNotes(String clinicalNotes) { this.clinicalNotes = clinicalNotes; }
    public String getDiagnosis() { return diagnosis; }
    public void setDiagnosis(String diagnosis) { this.diagnosis = diagnosis; }
    public EncounterStatus getStatus() { return status; }
    public void setStatus(EncounterStatus status) { this.status = status; }
    public java.time.Instant getSignedAt() { return signedAt; }
    public void sign() { this.status = EncounterStatus.SIGNED; this.signedAt = java.time.Instant.now(); }
}
