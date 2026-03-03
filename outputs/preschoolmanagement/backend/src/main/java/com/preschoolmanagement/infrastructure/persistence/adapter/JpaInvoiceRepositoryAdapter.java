package com.preschoolmanagement.infrastructure.persistence.adapter;

import com.preschoolmanagement.domain.model.Invoice;
import com.preschoolmanagement.domain.repository.InvoiceRepository;
import com.preschoolmanagement.domain.valueobject.InvoiceId;
import com.preschoolmanagement.infrastructure.persistence.entity.InvoiceJpaEntity;
import com.preschoolmanagement.infrastructure.persistence.spring.SpringDataInvoiceRepository;
import org.springframework.stereotype.Repository;

import java.util.Objects;
import java.util.Optional;

@Repository
public class JpaInvoiceRepositoryAdapter implements InvoiceRepository {

    private final SpringDataInvoiceRepository repo;

    public JpaInvoiceRepositoryAdapter(SpringDataInvoiceRepository repo) {
        this.repo = Objects.requireNonNull(repo);
    }

    @Override
    public Invoice save(Invoice invoice) {
        InvoiceJpaEntity entity = new InvoiceJpaEntity(
                invoice.id().value(),
                invoice.invoiceNumber(),
                invoice.amount(),
                invoice.status(),
                invoice.issuedDate(),
                invoice.dueDate(),
                invoice.paidDate(),
                invoice.childId().value(),
                invoice.parentId().value()
        );
        InvoiceJpaEntity saved = repo.save(entity);
        return new Invoice(
                new InvoiceId(saved.getId()),
                saved.getInvoiceNumber(),
                saved.getAmount(),
                saved.getStatus(),
                saved.getIssuedDate(),
                saved.getDueDate(),
                saved.getPaidDate(),
                saved.getChildId(),
                saved.getParentId()
        );
    }

    @Override
    public Optional<Invoice> findById(InvoiceId id) {
        return repo.findById(id.value())
                .map(e -> new Invoice(
                        new InvoiceId(e.getId()),
                        e.getInvoiceNumber(),
                        e.getAmount(),
                        e.getStatus(),
                        e.getIssuedDate(),
                        e.getDueDate(),
                        e.getPaidDate(),
                        e.getChildId(),
                        e.getParentId()
                ));
    }
}
