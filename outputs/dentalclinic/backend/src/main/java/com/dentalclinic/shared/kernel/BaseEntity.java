package com.dentalclinic.shared.kernel;

import jakarta.persistence.*;
import java.time.Instant;
import java.util.UUID;

@MappedSuperclass
public abstract class BaseEntity {
    @Id
    @Column(columnDefinition = "uuid", updatable = false, nullable = false)
    private UUID id = UUID.randomUUID();

    @Column(name = "clinic_id", nullable = false, columnDefinition = "uuid")
    private UUID clinicId;

    @Column(name = "created_at", nullable = false, updatable = false)
    private Instant createdAt = Instant.now();

    @Column(name = "updated_at", nullable = false)
    private Instant updatedAt = Instant.now();

    @Version
    @Column(nullable = false)
    private Long version = 0L;

    @Column(name = "deleted", nullable = false)
    private boolean deleted = false;

    @PreUpdate
    void onUpdate() { this.updatedAt = Instant.now(); }

    public UUID getId() { return id; }
    public void setId(UUID id) { this.id = id; }
    public UUID getClinicId() { return clinicId; }
    public void setClinicId(UUID clinicId) { this.clinicId = clinicId; }
    public Instant getCreatedAt() { return createdAt; }
    public Instant getUpdatedAt() { return updatedAt; }
    public Long getVersion() { return version; }
    public boolean isDeleted() { return deleted; }
    public void setDeleted(boolean deleted) { this.deleted = deleted; }
}
