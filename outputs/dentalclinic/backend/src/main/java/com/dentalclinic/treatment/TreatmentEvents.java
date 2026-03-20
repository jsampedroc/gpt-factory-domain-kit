package com.dentalclinic.treatment;

import java.math.BigDecimal;
import java.util.UUID;

public final class TreatmentEvents {
    public record TreatmentPlanCreated(UUID planId, UUID patientId, UUID clinicId, String title) {}
    public record TreatmentPlanAccepted(UUID planId, UUID patientId, UUID clinicId, BigDecimal totalAmount) {}
    public record TreatmentPlanCancelled(UUID planId, UUID patientId, UUID clinicId) {}
    private TreatmentEvents() {}
}
