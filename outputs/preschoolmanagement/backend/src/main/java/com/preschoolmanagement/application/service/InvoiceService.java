package com.preschoolmanagement.application.service;

import com.preschoolmanagement.domain.model.Invoice;
import com.preschoolmanagement.domain.repository.InvoiceRepository;
import com.preschoolmanagement.domain.valueobject.InvoiceId;

public class InvoiceService {

    private final InvoiceRepository repository;

    public InvoiceService(InvoiceRepository repository) {
        this.repository = repository;
    }

    public Invoice findById(InvoiceId id) {
        return repository.findById(id)
                .orElseThrow(() -> new IllegalArgumentException("Invoice not found"));
    }

    public void save(Invoice invoice) {
        repository.save(invoice);
    }
}
