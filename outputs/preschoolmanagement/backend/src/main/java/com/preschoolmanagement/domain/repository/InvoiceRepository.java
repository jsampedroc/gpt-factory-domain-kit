package com.preschoolmanagement.domain.repository;

import com.preschoolmanagement.domain.model.Invoice;
import com.preschoolmanagement.domain.valueobject.InvoiceId;

import java.util.Optional;

public interface InvoiceRepository {

    Optional<Invoice> findById(InvoiceId id);

    void save(Invoice entity);
}
