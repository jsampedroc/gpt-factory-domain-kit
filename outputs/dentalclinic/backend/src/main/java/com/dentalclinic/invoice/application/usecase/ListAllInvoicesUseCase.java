package com.dentalclinic.invoice.application.usecase;

import com.dentalclinic.shared.PageResult;
import com.dentalclinic.invoice.domain.model.Invoice;
import com.dentalclinic.invoice.domain.repository.InvoiceRepository;
import org.springframework.stereotype.Service;

/**
 * Returns a paginated, searchable list of Invoice records.
 */
@Service
public class ListAllInvoicesUseCase {

    private final InvoiceRepository repository;

    public ListAllInvoicesUseCase(InvoiceRepository repository) {
        this.repository = repository;
    }

    public PageResult<Invoice> execute(ListAllInvoicesQuery query) {
        return repository.findAll(query.page(), query.size(), query.search());
    }
}
