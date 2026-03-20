package com.dentalclinic.patient.domain.event;

import com.dentalclinic.shared.DomainEvent;
import java.time.Instant;
import java.util.UUID;

public record PatientRegisteredEvent(
        UUID eventId,
        Instant occurredOn,
        UUID patientId,
        String firstName,
        String lastName
) implements DomainEvent {
    public static PatientRegisteredEvent of(UUID patientId, String firstName, String lastName) {
        return new PatientRegisteredEvent(UUID.randomUUID(), Instant.now(), patientId, firstName, lastName);
    }
    @Override public String eventType() { return "patient.registered"; }
}
