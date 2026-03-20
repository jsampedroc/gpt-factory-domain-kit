package com.dentalclinic.shared;

import org.springframework.stereotype.Service;

/**
 * Records audit events for domain entities.
 * Call from use cases after successful state changes.
 */
@Service
public class AuditService {

    private final AuditLogRepository repository;

    public AuditService(AuditLogRepository repository) {
        this.repository = repository;
    }

    public void record(String entityType, String entityId,
                       String action, String performedBy, String details) {
        repository.save(new AuditLog(entityType, entityId, action, performedBy, details));
    }

    public void recordCreate(String entityType, String entityId, String performedBy) {
        record(entityType, entityId, "CREATE", performedBy, null);
    }

    public void recordUpdate(String entityType, String entityId, String performedBy, String changes) {
        record(entityType, entityId, "UPDATE", performedBy, changes);
    }

    public void recordDelete(String entityType, String entityId, String performedBy) {
        record(entityType, entityId, "DELETE", performedBy, null);
    }
}
