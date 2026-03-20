package com.dentalclinic.treatment.infrastructure.persistence.entity;

import com.dentalclinic.shared.kernel.BaseEntity;
import jakarta.persistence.*;
import java.math.BigDecimal;
import java.time.LocalDate;
import java.util.UUID;

@Entity
@Table(name = "treat_plan")
public class TreatmentJpaEntity extends BaseEntity {

    @Column(name = "patient_id", nullable = false, columnDefinition = "uuid")
    private UUID patientId;

    @Column(name = "patient_name", length = 200)
    private String patientName;

    @Column(name = "practitioner_id", columnDefinition = "uuid")
    private UUID practitionerId;

    @Column(name = "title", nullable = false, length = 300)
    private String title;

    @Column(name = "description")
    private String description;

    @Column(name = "total_amount", nullable = false, precision = 10, scale = 2)
    private BigDecimal totalAmount = BigDecimal.ZERO;

    @Column(name = "status", nullable = false, length = 30)
    private String status = "DRAFT";

    @Column(name = "accepted_date")
    private LocalDate acceptedDate;

    public TreatmentJpaEntity() {}

    public UUID getPatientId() { return patientId; }
    public void setPatientId(UUID patientId) { this.patientId = patientId; }

    public String getPatientName() { return patientName; }
    public void setPatientName(String patientName) { this.patientName = patientName; }

    public UUID getPractitionerId() { return practitionerId; }
    public void setPractitionerId(UUID practitionerId) { this.practitionerId = practitionerId; }

    public String getTitle() { return title; }
    public void setTitle(String title) { this.title = title; }

    public String getDescription() { return description; }
    public void setDescription(String description) { this.description = description; }

    public BigDecimal getTotalAmount() { return totalAmount; }
    public void setTotalAmount(BigDecimal totalAmount) { this.totalAmount = totalAmount; }

    public String getStatus() { return status; }
    public void setStatus(String status) { this.status = status; }

    public LocalDate getAcceptedDate() { return acceptedDate; }
    public void setAcceptedDate(LocalDate acceptedDate) { this.acceptedDate = acceptedDate; }

    // Legacy compat
    public UUID getTreatmentId() { return getId(); }
    public void setTreatmentId(UUID id) { setId(id); }

    public UUID getAppointmentId() { return null; }
    public void setAppointmentId(UUID appointmentId) { /* not stored in treat_plan */ }

    public BigDecimal getCost() { return totalAmount; }
    public void setCost(BigDecimal cost) { this.totalAmount = cost; }

    public boolean isActive() { return !isDeleted(); }
    public void setActive(boolean active) { setDeleted(!active); }
}
