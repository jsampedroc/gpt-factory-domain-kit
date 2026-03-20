package com.dentalclinic.invoice.domain.service;

import com.dentalclinic.domain.valueobject.Money;
import com.dentalclinic.invoice.domain.model.Invoice;
import com.dentalclinic.invoice.domain.repository.InvoiceRepository;
import com.dentalclinic.invoice.domain.valueobject.InvoiceStatus;
import java.time.LocalDate;
import java.util.UUID;

public class InvoiceDomainService {

    private final InvoiceRepository repository;

    public InvoiceDomainService(InvoiceRepository repository) {
        this.repository = repository;
    }

}
