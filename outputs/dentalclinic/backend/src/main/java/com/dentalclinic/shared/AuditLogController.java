package com.dentalclinic.shared;

import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;

import java.util.UUID;

/**
 * REST endpoint for querying the audit log.
 * Restricted to ADMIN role.
 */
@RestController
@RequestMapping("/api/audit")
@Tag(name = "Audit Log", description = "Query audit trail — Admin only")
@PreAuthorize("hasRole('ADMIN')")
public class AuditLogController {

    private final AuditLogRepository repository;

    public AuditLogController(AuditLogRepository repository) {
        this.repository = repository;
    }

    @GetMapping("/entity/{type}/{id}")
    @Operation(summary = "Get audit history for a specific entity")
    public ResponseEntity<Page<AuditLog>> byEntity(
            @PathVariable String type,
            @PathVariable String id,
            Pageable pageable) {
        return ResponseEntity.ok(repository.findByEntityTypeAndEntityId(type, id, pageable));
    }

    @GetMapping("/user/{username}")
    @Operation(summary = "Get audit history for a specific user")
    public ResponseEntity<Page<AuditLog>> byUser(
            @PathVariable String username,
            Pageable pageable) {
        return ResponseEntity.ok(repository.findByPerformedBy(username, pageable));
    }
}
