package com.dentalclinic.appointment.domain.event;

import com.dentalclinic.shared.DomainEvent;
import java.time.Instant;
import java.util.UUID;

public record AppointmentCancelledEvent(
        UUID eventId,
        Instant occurredOn,
        UUID appointmentId
) implements DomainEvent {
    public static AppointmentCancelledEvent of(UUID appointmentId) {
        return new AppointmentCancelledEvent(UUID.randomUUID(), Instant.now(), appointmentId);
    }
    @Override public String eventType() { return "appointment.cancelled"; }
}
