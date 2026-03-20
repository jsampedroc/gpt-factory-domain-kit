package com.dentalclinic.shared.audit;

import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;
import java.util.UUID;

public interface AuditEventLogRepository extends JpaRepository<AuditEventLog, UUID> {
    List<AuditEventLog> findByClinicIdOrderByOccurredAtDesc(UUID clinicId);
    List<AuditEventLog> findByEntityTypeAndEntityIdOrderByOccurredAtDesc(String entityType, String entityId);
}
