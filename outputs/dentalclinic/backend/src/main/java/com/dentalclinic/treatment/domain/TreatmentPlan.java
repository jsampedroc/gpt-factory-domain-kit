package com.dentalclinic.treatment.domain;

import com.dentalclinic.shared.kernel.BaseEntity;
import jakarta.persistence.*;
import java.math.BigDecimal;
import java.time.LocalDate;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

@Entity
@Table(name = "treat_plan")
public class TreatmentPlan extends BaseEntity {

    @Column(name = "patient_id", nullable = false, columnDefinition = "uuid")
    private UUID patientId;

    @Column(name = "patient_name")
    private String patientName;

    @Column(name = "practitioner_id", columnDefinition = "uuid")
    private UUID practitionerId;

    @Column(name = "title", nullable = false)
    private String title;

    @Column(name = "description", columnDefinition = "text")
    private String description;

    @Column(name = "total_amount", precision = 10, scale = 2)
    private BigDecimal totalAmount = BigDecimal.ZERO;

    @Column(name = "status", nullable = false)
    @Enumerated(EnumType.STRING)
    private TreatmentPlanStatus status = TreatmentPlanStatus.DRAFT;

    @Column(name = "accepted_date")
    private LocalDate acceptedDate;

    @OneToMany(cascade = CascadeType.ALL, orphanRemoval = true)
    @JoinColumn(name = "plan_id")
    private List<TreatmentPlanItem> items = new ArrayList<>();

    protected TreatmentPlan() {}

    public TreatmentPlan(UUID patientId, String patientName, UUID practitionerId, String title, UUID clinicId) {
        this.patientId = patientId;
        this.patientName = patientName;
        this.practitionerId = practitionerId;
        this.title = title;
        setClinicId(clinicId);
    }

    public UUID getPatientId() { return patientId; }
    public String getPatientName() { return patientName; }
    public UUID getPractitionerId() { return practitionerId; }
    public String getTitle() { return title; }
    public void setTitle(String title) { this.title = title; }
    public String getDescription() { return description; }
    public void setDescription(String description) { this.description = description; }
    public BigDecimal getTotalAmount() { return totalAmount; }
    public void setTotalAmount(BigDecimal totalAmount) { this.totalAmount = totalAmount; }
    public TreatmentPlanStatus getStatus() { return status; }
    public void setStatus(TreatmentPlanStatus status) { this.status = status; }
    public LocalDate getAcceptedDate() { return acceptedDate; }
    public List<TreatmentPlanItem> getItems() { return items; }
    public void accept() { this.status = TreatmentPlanStatus.ACCEPTED; this.acceptedDate = LocalDate.now(); }
}
