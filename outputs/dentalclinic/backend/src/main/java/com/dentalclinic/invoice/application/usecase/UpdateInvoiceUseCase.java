package com.dentalclinic.invoice.application.usecase;

import com.dentalclinic.invoice.domain.model.Invoice;
import com.dentalclinic.invoice.domain.repository.InvoiceRepository;
import com.dentalclinic.invoice.domain.valueobject.InvoiceId;
import java.util.UUID;
import java.util.Optional;
import java.util.List;
import org.springframework.cache.annotation.CacheEvict;
import org.springframework.cache.annotation.Caching;
import org.springframework.stereotype.Service;

/**
 * Updates an existing Invoice
 */
@Service
public class UpdateInvoiceUseCase {

    private final InvoiceRepository repository;

    public UpdateInvoiceUseCase(InvoiceRepository repository) {
        this.repository = repository;
    }

    @Caching(evict = {
        @CacheEvict(value = "entityById", key = "#command.invoiceId()"),
        @CacheEvict(value = "dashboard", allEntries = true)
    })
    public Invoice execute(UpdateInvoiceCommand command) {
        return repository.findById(command.invoiceId())
            .orElseThrow(() -> new IllegalArgumentException("Not found"));
    }
}