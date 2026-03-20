package com.dentalclinic.shared.events;

import jakarta.persistence.*;
import java.time.Instant;
import java.util.UUID;

@Entity
@Table(name = "outbox_event")
public class OutboxEvent {
    @Id
    @Column(columnDefinition = "uuid")
    private UUID id = UUID.randomUUID();

    @Column(name = "aggregate_type", nullable = false)
    private String aggregateType;

    @Column(name = "aggregate_id", nullable = false)
    private String aggregateId;

    @Column(name = "event_type", nullable = false)
    private String eventType;

    @Column(name = "payload", columnDefinition = "text", nullable = false)
    private String payload;

    @Column(name = "created_at", nullable = false)
    private Instant createdAt = Instant.now();

    @Column(name = "published", nullable = false)
    private boolean published = false;

    @Column(name = "published_at")
    private Instant publishedAt;

    public OutboxEvent(String aggregateType, String aggregateId, String eventType, String payload) {
        this.aggregateType = aggregateType;
        this.aggregateId = aggregateId;
        this.eventType = eventType;
        this.payload = payload;
    }
    protected OutboxEvent() {}

    public UUID getId() { return id; }
    public String getAggregateType() { return aggregateType; }
    public String getAggregateId() { return aggregateId; }
    public String getEventType() { return eventType; }
    public String getPayload() { return payload; }
    public Instant getCreatedAt() { return createdAt; }
    public boolean isPublished() { return published; }
    public void markPublished() { this.published = true; this.publishedAt = Instant.now(); }
}
