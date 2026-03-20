package com.dentalclinic.shared;

import java.time.Instant;
import java.util.UUID;

/**
 * Marker interface for all domain events.
 * Events are immutable records published after a state change.
 */
public interface DomainEvent {
    UUID eventId();
    Instant occurredOn();
    String eventType();
}
