package com.dentalclinic.patient;

import java.util.UUID;

public final class PatientEvents {
    public record PatientCreated(UUID patientId, UUID clinicId, String fullName) {}
    public record PatientUpdated(UUID patientId, UUID clinicId) {}
    public record PatientFlagged(UUID patientId, UUID clinicId, String alertText) {}
    private PatientEvents() {}
}
