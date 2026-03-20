package com.dentalclinic.shared.audit;

import jakarta.persistence.*;
import java.time.Instant;
import java.util.UUID;

@Entity
@Table(name = "audit_event_log")
public class AuditEventLog {
    @Id
    @Column(columnDefinition = "uuid")
    private UUID id = UUID.randomUUID();

    @Column(name = "clinic_id", columnDefinition = "uuid", nullable = false)
    private UUID clinicId;

    @Column(name = "user_id")
    private String userId;

    @Column(name = "action", nullable = false)
    private String action;

    @Column(name = "entity_type")
    private String entityType;

    @Column(name = "entity_id")
    private String entityId;

    @Column(name = "detail", columnDefinition = "text")
    private String detail;

    @Column(name = "ip_address")
    private String ipAddress;

    @Column(name = "occurred_at", nullable = false)
    private Instant occurredAt = Instant.now();

    public AuditEventLog(UUID clinicId, String userId, String action, String entityType, String entityId, String detail) {
        this.clinicId = clinicId;
        this.userId = userId;
        this.action = action;
        this.entityType = entityType;
        this.entityId = entityId;
        this.detail = detail;
    }
    protected AuditEventLog() {}

    public UUID getId() { return id; }
    public UUID getClinicId() { return clinicId; }
    public String getUserId() { return userId; }
    public String getAction() { return action; }
    public String getEntityType() { return entityType; }
    public String getEntityId() { return entityId; }
    public String getDetail() { return detail; }
    public Instant getOccurredAt() { return occurredAt; }
}
