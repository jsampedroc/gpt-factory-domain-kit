package com.dentalclinic.scheduling.domain;

import com.dentalclinic.shared.kernel.BaseEntity;
import jakarta.persistence.*;
import java.time.LocalDateTime;
import java.util.UUID;

@Entity
@Table(name = "sched_appointment")
public class Appointment extends BaseEntity {

    @Column(name = "patient_id", nullable = false, columnDefinition = "uuid")
    private UUID patientId;

    @Column(name = "patient_name")
    private String patientName;

    @Column(name = "practitioner_id", columnDefinition = "uuid")
    private UUID practitionerId;

    @Column(name = "practitioner_name")
    private String practitionerName;

    @Column(name = "chair_id")
    private String chairId;

    @Column(name = "start_time", nullable = false)
    private LocalDateTime startTime;

    @Column(name = "end_time", nullable = false)
    private LocalDateTime endTime;

    @Column(name = "procedure_name")
    private String procedureName;

    @Column(name = "status", nullable = false)
    @Enumerated(EnumType.STRING)
    private AppointmentStatus status = AppointmentStatus.BOOKED;

    @Column(name = "notes", columnDefinition = "text")
    private String notes;

    @Column(name = "reminder_sent", nullable = false)
    private boolean reminderSent = false;

    protected Appointment() {}

    public Appointment(UUID patientId, String patientName, UUID practitionerId, String practitionerName,
                       LocalDateTime startTime, LocalDateTime endTime, String procedureName, UUID clinicId) {
        this.patientId = patientId;
        this.patientName = patientName;
        this.practitionerId = practitionerId;
        this.practitionerName = practitionerName;
        this.startTime = startTime;
        this.endTime = endTime;
        this.procedureName = procedureName;
        setClinicId(clinicId);
    }

    public UUID getPatientId() { return patientId; }
    public String getPatientName() { return patientName; }
    public UUID getPractitionerId() { return practitionerId; }
    public String getPractitionerName() { return practitionerName; }
    public String getChairId() { return chairId; }
    public void setChairId(String chairId) { this.chairId = chairId; }
    public LocalDateTime getStartTime() { return startTime; }
    public void setStartTime(LocalDateTime startTime) { this.startTime = startTime; }
    public LocalDateTime getEndTime() { return endTime; }
    public void setEndTime(LocalDateTime endTime) { this.endTime = endTime; }
    public String getProcedureName() { return procedureName; }
    public void setProcedureName(String procedureName) { this.procedureName = procedureName; }
    public AppointmentStatus getStatus() { return status; }
    public void setStatus(AppointmentStatus status) { this.status = status; }
    public String getNotes() { return notes; }
    public void setNotes(String notes) { this.notes = notes; }
    public boolean isReminderSent() { return reminderSent; }
    public void setReminderSent(boolean reminderSent) { this.reminderSent = reminderSent; }
}
