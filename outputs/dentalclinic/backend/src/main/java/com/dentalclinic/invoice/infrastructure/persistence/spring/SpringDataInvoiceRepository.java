package com.dentalclinic.invoice.infrastructure.persistence.spring;

import com.dentalclinic.invoice.infrastructure.persistence.entity.InvoiceJpaEntity;
import java.util.List;
import java.util.UUID;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.JpaSpecificationExecutor;

public interface SpringDataInvoiceRepository
        extends JpaRepository<InvoiceJpaEntity, UUID>,
                JpaSpecificationExecutor<InvoiceJpaEntity> {

    List<InvoiceJpaEntity> findByClinicIdAndDeletedFalse(UUID clinicId);

    long countByDeletedFalse();
}
