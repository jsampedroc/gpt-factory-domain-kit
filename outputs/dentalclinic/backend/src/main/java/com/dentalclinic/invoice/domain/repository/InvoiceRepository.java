package com.dentalclinic.invoice.domain.repository;

import com.dentalclinic.shared.PageResult;
import com.dentalclinic.invoice.domain.model.Invoice;
import java.util.Optional;
import java.util.UUID;

public interface InvoiceRepository {

    Invoice save(Invoice entity);

    Optional<Invoice> findById(UUID id);

    PageResult<Invoice> findAll(int page, int size, String search);

    void deactivate(UUID id);

}
