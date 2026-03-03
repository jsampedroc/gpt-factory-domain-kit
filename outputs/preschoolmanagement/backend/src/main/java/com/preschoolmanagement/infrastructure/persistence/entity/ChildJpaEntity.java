package com.preschoolmanagement.infrastructure.persistence.entity;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;

import java.util.UUID;

@Entity
@Table(name = "children")
public class ChildJpaEntity {

    @Id
    @Column(name = "id", nullable = false, updatable = false)
    private UUID id;

    protected ChildJpaEntity() {
    }

    public ChildJpaEntity(UUID id) {
        this.id = id;
    }

    public UUID getId() {
        return id;
    }
}
