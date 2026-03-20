package com.dentalclinic.appointment.domain.model;

import com.dentalclinic.appointment.domain.valueobject.AppointmentId;
import com.dentalclinic.appointment.domain.valueobject.AppointmentStatus;
import com.dentalclinic.domain.shared.Entity;
import java.time.Instant;
import java.time.LocalDateTime;
import java.util.UUID;

public class Appointment extends Entity<AppointmentId> {

    private final UUID patientId;
    private final String patientName;
    private final UUID practitionerId;
    private final String practitionerName;
    private final LocalDateTime startTime;
    private final LocalDateTime endTime;
    private final String procedureName;
    private final AppointmentStatus status;
    private final String notes;
    private final UUID clinicId;
    private final Instant createdAt;

    public Appointment(AppointmentId id, UUID patientId, String patientName,
                       UUID practitionerId, String practitionerName,
                       LocalDateTime startTime, LocalDateTime endTime,
                       String procedureName, AppointmentStatus status,
                       String notes, UUID clinicId, Instant createdAt) {
        super(id);
        this.patientId = patientId;
        this.patientName = patientName;
        this.practitionerId = practitionerId;
        this.practitionerName = practitionerName;
        this.startTime = startTime;
        this.endTime = endTime;
        this.procedureName = procedureName;
        this.status = status;
        this.notes = notes;
        this.clinicId = clinicId;
        this.createdAt = createdAt;
    }

    public UUID getPatientId() { return patientId; }
    public String getPatientName() { return patientName; }
    public UUID getPractitionerId() { return practitionerId; }
    public String getPractitionerName() { return practitionerName; }
    public LocalDateTime getStartTime() { return startTime; }
    public LocalDateTime getEndTime() { return endTime; }
    public String getProcedureName() { return procedureName; }
    public AppointmentStatus getStatus() { return status; }
    public String getNotes() { return notes; }
    public UUID getClinicId() { return clinicId; }
    public Instant getCreatedAt() { return createdAt; }

    // Legacy compat
    public UUID getAppointmentId() { return getId().value(); }
    public UUID getDentistId() { return practitionerId; }
    public LocalDateTime getAppointmentDate() { return startTime; }
}
