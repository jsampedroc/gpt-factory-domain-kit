package com.dentalclinic.shared;

import jakarta.persistence.*;
import jakarta.validation.constraints.NotNull;
import java.math.BigDecimal;
import java.time.LocalDate;
import java.util.UUID;

@Entity
@Table(name = "treatment_plans")
public class TreatmentPlan {

    @Id @GeneratedValue(strategy = GenerationType.UUID)
    private UUID id;

    @NotNull @Column(name = "patient_id", nullable = false)
    private UUID patientId;

    @Column(name = "dentist_id")
    private UUID dentistId;

    /** DRAFT | PRESENTED | ACCEPTED | REJECTED | COMPLETED */
    @Column(name = "status", nullable = false, length = 20)
    private String status = "DRAFT";

    @Column(name = "total_amount", precision = 10, scale = 2)
    private BigDecimal totalAmount = BigDecimal.ZERO;

    @Column(name = "created_at")
    private LocalDate createdAt = LocalDate.now();

    @Column(name = "expires_at")
    private LocalDate expiresAt;

    @Column(name = "notes", length = 1000)
    private String notes;

    protected TreatmentPlan() {}

    public TreatmentPlan(UUID patientId, UUID dentistId, LocalDate expiresAt, String notes) {
        this.patientId = patientId;
        this.dentistId = dentistId;
        this.expiresAt = expiresAt;
        this.notes = notes;
    }

    public UUID getId() { return id; }
    public UUID getPatientId() { return patientId; }
    public UUID getDentistId() { return dentistId; }
    public String getStatus() { return status; }
    public void setStatus(String status) { this.status = status; }
    public BigDecimal getTotalAmount() { return totalAmount; }
    public void setTotalAmount(BigDecimal totalAmount) { this.totalAmount = totalAmount; }
    public LocalDate getCreatedAt() { return createdAt; }
    public LocalDate getExpiresAt() { return expiresAt; }
    public String getNotes() { return notes; }
}
