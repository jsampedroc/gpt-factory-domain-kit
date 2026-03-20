package com.dentalclinic.invoice.application.usecase;

import com.dentalclinic.invoice.domain.model.Invoice;
import com.dentalclinic.invoice.domain.repository.InvoiceRepository;
import com.dentalclinic.invoice.domain.valueobject.InvoiceId;
import java.util.UUID;
import java.util.Optional;
import java.util.List;
import org.springframework.cache.annotation.Cacheable;
import org.springframework.stereotype.Service;

/**
 * Retrieves a Invoice by its identifier
 */
@Service
public class GetInvoiceByIdUseCase {

    private final InvoiceRepository repository;

    public GetInvoiceByIdUseCase(InvoiceRepository repository) {
        this.repository = repository;
    }

    @Cacheable(value = "entityById", key = "#query.invoiceId()")
    public Optional<Invoice> execute(GetInvoiceByIdQuery query) {
        return repository.findById(query.invoiceId());
    }
}