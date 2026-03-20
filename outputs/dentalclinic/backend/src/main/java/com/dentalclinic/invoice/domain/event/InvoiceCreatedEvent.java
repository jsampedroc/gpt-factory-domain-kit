package com.dentalclinic.invoice.domain.event;

import com.dentalclinic.shared.DomainEvent;
import java.time.Instant;
import java.util.UUID;

public record InvoiceCreatedEvent(
        UUID eventId,
        Instant occurredOn,
        UUID invoiceId,
        UUID patientId
) implements DomainEvent {
    public static InvoiceCreatedEvent of(UUID invoiceId, UUID patientId) {
        return new InvoiceCreatedEvent(UUID.randomUUID(), Instant.now(), invoiceId, patientId);
    }
    @Override public String eventType() { return "invoice.created"; }
}
