package com.dentalclinic.treatment.domain.model;

import com.dentalclinic.domain.shared.Entity;
import com.dentalclinic.domain.valueobject.Money;
import com.dentalclinic.treatment.domain.valueobject.TreatmentId;
import java.math.BigDecimal;
import java.time.Instant;
import java.time.LocalDate;
import java.util.UUID;

public class Treatment extends Entity<TreatmentId> {

    private final UUID patientId;
    private final String patientName;
    private final UUID practitionerId;
    private final String title;
    private final String description;
    private final BigDecimal totalAmount;
    private final String status;
    private final LocalDate acceptedDate;
    private final Money cost;
    private final UUID clinicId;
    private final Instant createdAt;

    public Treatment(TreatmentId id, UUID patientId, String patientName,
                     UUID practitionerId, String title, String description,
                     BigDecimal totalAmount, String status, LocalDate acceptedDate,
                     UUID clinicId, Instant createdAt) {
        super(id);
        this.patientId = patientId;
        this.patientName = patientName;
        this.practitionerId = practitionerId;
        this.title = title;
        this.description = description;
        this.totalAmount = totalAmount != null ? totalAmount : BigDecimal.ZERO;
        this.status = status != null ? status : "DRAFT";
        this.acceptedDate = acceptedDate;
        this.clinicId = clinicId;
        this.createdAt = createdAt;
        this.cost = new Money(this.totalAmount.doubleValue(), "USD");
    }

    // Legacy compat constructor
    public Treatment(TreatmentId id, UUID treatmentId, UUID appointmentId,
                     String description, Money cost) {
        this(id, null, null, null,
             description != null ? description : "Treatment",
             description,
             cost != null ? BigDecimal.valueOf(cost.getAmount()) : BigDecimal.ZERO,
             "DRAFT", null, null, null);
    }

    public UUID getPatientId() { return patientId; }
    public String getPatientName() { return patientName; }
    public UUID getPractitionerId() { return practitionerId; }
    public String getTitle() { return title; }
    public String getDescription() { return description; }
    public BigDecimal getTotalAmount() { return totalAmount; }
    public String getStatus() { return status; }
    public LocalDate getAcceptedDate() { return acceptedDate; }
    public Money getCost() { return cost; }
    public UUID getClinicId() { return clinicId; }
    public Instant getCreatedAt() { return createdAt; }

    // Legacy compat
    public UUID getTreatmentId() { return getId().value(); }
    public UUID getAppointmentId() { return null; }
}
