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
 * Deactivates a Invoice record
 */
@Service
public class DeactivateInvoiceUseCase {

    private final InvoiceRepository repository;

    public DeactivateInvoiceUseCase(InvoiceRepository repository) {
        this.repository = repository;
    }

    @Caching(evict = {
        @CacheEvict(value = "entityById", allEntries = true),
        @CacheEvict(value = "dashboard", allEntries = true)
    })
    public void execute(DeactivateInvoiceCommand command) {
        repository.deactivate(command.invoiceId());
    }
}