package com.dentalclinic.dentist.domain.event;

import com.dentalclinic.shared.DomainEvent;
import java.time.Instant;
import java.util.UUID;

public record DentistRegisteredEvent(
        UUID eventId,
        Instant occurredOn,
        UUID dentistId,
        String firstName,
        String lastName,
        String licenseNumber
) implements DomainEvent {
    public static DentistRegisteredEvent of(UUID dentistId, String firstName, String lastName, String licenseNumber) {
        return new DentistRegisteredEvent(UUID.randomUUID(), Instant.now(), dentistId, firstName, lastName, licenseNumber);
    }
    @Override public String eventType() { return "dentist.registered"; }
}
