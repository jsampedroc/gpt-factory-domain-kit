package com.dentalclinic.appointment.domain.event;

import com.dentalclinic.shared.DomainEvent;
import java.time.Instant;
import java.time.LocalDateTime;
import java.util.UUID;

public record AppointmentScheduledEvent(
        UUID eventId,
        Instant occurredOn,
        UUID appointmentId,
        UUID patientId,
        UUID dentistId,
        LocalDateTime appointmentDate
) implements DomainEvent {
    public static AppointmentScheduledEvent of(UUID appointmentId, UUID patientId, UUID dentistId, LocalDateTime date) {
        return new AppointmentScheduledEvent(UUID.randomUUID(), Instant.now(), appointmentId, patientId, dentistId, date);
    }
    @Override public String eventType() { return "appointment.scheduled"; }
}
