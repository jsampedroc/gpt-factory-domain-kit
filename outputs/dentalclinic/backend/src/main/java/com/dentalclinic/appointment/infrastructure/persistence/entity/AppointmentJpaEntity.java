package com.dentalclinic.appointment.infrastructure.persistence.entity;

import com.dentalclinic.shared.kernel.BaseEntity;
import jakarta.persistence.*;
import java.time.LocalDateTime;
import java.util.UUID;

@Entity
@Table(name = "sched_appointment")
public class AppointmentJpaEntity extends BaseEntity {

    @Column(name = "patient_id", nullable = false, columnDefinition = "uuid")
    private UUID patientId;

    @Column(name = "patient_name", length = 200)
    private String patientName;

    @Column(name = "practitioner_id", columnDefinition = "uuid")
    private UUID practitionerId;

    @Column(name = "practitioner_name", length = 200)
    private String practitionerName;

    @Column(name = "chair_id", length = 50)
    private String chairId;

    @Column(name = "start_time", nullable = false)
    private LocalDateTime startTime;

    @Column(name = "end_time", nullable = false)
    private LocalDateTime endTime;

    @Column(name = "procedure_name", length = 200)
    private String procedureName;

    @Column(name = "status", nullable = false, length = 30)
    private String status = "BOOKED";

    @Column(name = "notes")
    private String notes;

    @Column(name = "reminder_sent", nullable = false)
    private boolean reminderSent = false;

    public AppointmentJpaEntity() {}

    public UUID getPatientId() { return patientId; }
    public void setPatientId(UUID patientId) { this.patientId = patientId; }

    public String getPatientName() { return patientName; }
    public void setPatientName(String patientName) { this.patientName = patientName; }

    public UUID getPractitionerId() { return practitionerId; }
    public void setPractitionerId(UUID practitionerId) { this.practitionerId = practitionerId; }

    public String getPractitionerName() { return practitionerName; }
    public void setPractitionerName(String practitionerName) { this.practitionerName = practitionerName; }

    public String getChairId() { return chairId; }
    public void setChairId(String chairId) { this.chairId = chairId; }

    public LocalDateTime getStartTime() { return startTime; }
    public void setStartTime(LocalDateTime startTime) { this.startTime = startTime; }

    public LocalDateTime getEndTime() { return endTime; }
    public void setEndTime(LocalDateTime endTime) { this.endTime = endTime; }

    public String getProcedureName() { return procedureName; }
    public void setProcedureName(String procedureName) { this.procedureName = procedureName; }

    public String getStatus() { return status; }
    public void setStatus(String status) { this.status = status; }

    public String getNotes() { return notes; }
    public void setNotes(String notes) { this.notes = notes; }

    public boolean isReminderSent() { return reminderSent; }
    public void setReminderSent(boolean reminderSent) { this.reminderSent = reminderSent; }

    // Legacy compat getters/setters for old fields used by adapter
    public UUID getAppointmentId() { return getId(); }
    public void setAppointmentId(UUID id) { setId(id); }

    public UUID getDentistId() { return practitionerId; }
    public void setDentistId(UUID dentistId) { this.practitionerId = dentistId; }

    public LocalDateTime getAppointmentDate() { return startTime; }
    public void setAppointmentDate(LocalDateTime date) { this.startTime = date; }

    public boolean isActive() { return !isDeleted(); }
    public void setActive(boolean active) { setDeleted(!active); }
}
