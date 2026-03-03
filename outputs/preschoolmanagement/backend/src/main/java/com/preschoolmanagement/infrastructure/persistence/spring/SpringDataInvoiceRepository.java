package com.preschoolmanagement.infrastructure.persistence.spring;

import com.preschoolmanagement.infrastructure.persistence.entity.InvoiceJpaEntity;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.UUID;

public interface SpringDataInvoiceRepository extends JpaRepository<InvoiceJpaEntity, UUID> {
}
