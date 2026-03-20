package com.dentalclinic.shared;

import jakarta.persistence.*;
import java.time.Instant;
import java.util.UUID;

/**
 * Persists every CREATE/UPDATE/DELETE action for auditing purposes.
 * Records who did what, when, and on which entity.
 */
@Entity
@Table(name = "audit_log", indexes = {
    @Index(name = "idx_audit_entity", columnList = "entity_type, entity_id"),
    @Index(name = "idx_audit_user", columnList = "performed_by"),
})
public class AuditLog {

    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private UUID id;

    @Column(name = "entity_type", nullable = false, length = 64)
    private String entityType;

    @Column(name = "entity_id", length = 64)
    private String entityId;

    @Column(name = "action", nullable = false, length = 16)
    private String action; // CREATE | UPDATE | DELETE

    @Column(name = "performed_by", length = 128)
    private String performedBy;

    @Column(name = "performed_at", nullable = false)
    private Instant performedAt = Instant.now();

    @Column(name = "details", length = 2000)
    private String details;

    protected AuditLog() {}

    public AuditLog(String entityType, String entityId, String action,
                    String performedBy, String details) {
        this.entityType = entityType;
        this.entityId = entityId;
        this.action = action;
        this.performedBy = performedBy;
        this.performedAt = Instant.now();
        this.details = details;
    }

    public UUID getId() { return id; }
    public String getEntityType() { return entityType; }
    public String getEntityId() { return entityId; }
    public String getAction() { return action; }
    public String getPerformedBy() { return performedBy; }
    public Instant getPerformedAt() { return performedAt; }
    public String getDetails() { return details; }
}
