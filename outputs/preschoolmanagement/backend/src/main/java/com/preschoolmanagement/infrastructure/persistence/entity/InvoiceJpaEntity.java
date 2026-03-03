package com.preschoolmanagement.infrastructure.persistence.entity;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;

import java.util.UUID;

@Entity
@Table(name = "invoices")
public class InvoiceJpaEntity {

    @Id
    @Column(name = "id", nullable = false, updatable = false)
    private UUID id;

    protected InvoiceJpaEntity() {
    }

    public InvoiceJpaEntity(UUID id) {
        this.id = id;
    }

    public UUID getId() {
        return id;
    }
}
