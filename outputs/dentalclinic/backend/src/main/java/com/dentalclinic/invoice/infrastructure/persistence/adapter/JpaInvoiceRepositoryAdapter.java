package com.dentalclinic.invoice.infrastructure.persistence.adapter;

import com.dentalclinic.shared.PageResult;
import com.dentalclinic.invoice.domain.model.Invoice;
import com.dentalclinic.invoice.domain.repository.InvoiceRepository;
import com.dentalclinic.invoice.domain.valueobject.InvoiceId;
import com.dentalclinic.invoice.domain.valueobject.InvoiceStatus;
import com.dentalclinic.invoice.infrastructure.persistence.entity.InvoiceJpaEntity;
import com.dentalclinic.invoice.infrastructure.persistence.spring.SpringDataInvoiceRepository;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.jpa.domain.Specification;
import org.springframework.stereotype.Repository;
import java.math.BigDecimal;
import java.time.LocalDate;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import java.util.stream.Collectors;
import com.dentalclinic.domain.valueobject.Money;

@Repository
public class JpaInvoiceRepositoryAdapter implements InvoiceRepository {

    private final SpringDataInvoiceRepository springRepository;

    public JpaInvoiceRepositoryAdapter(SpringDataInvoiceRepository springRepository) {
        this.springRepository = springRepository;
    }

    @Override
    public Invoice save(Invoice entity) {
        InvoiceJpaEntity jpa = toJpaEntity(entity);
        return toDomain(springRepository.save(jpa));
    }

    @Override
    public Optional<Invoice> findById(UUID id) {
        return springRepository.findById(id).map(this::toDomain);
    }

    @Override
    public PageResult<Invoice> findAll(int page, int size, String search) {
        Specification<InvoiceJpaEntity> spec = Specification.where(null);
        spec = spec.and((root, q, cb) -> cb.isFalse(root.get("deleted")));
        if (search != null && !search.isBlank()) {
            String like = "%" + search.toLowerCase() + "%";
            spec = spec.and((root, query, cb) ->
                cb.like(cb.lower(root.get("status")), like));
        }

        var result = springRepository.findAll(spec, PageRequest.of(page, size));

        List<Invoice> content = result.getContent().stream()
                .map(this::toDomain)
                .collect(Collectors.toList());

        return new PageResult<>(content, result.getNumber(), result.getSize(), result.getTotalElements());
    }

    @Override
    public void deactivate(UUID id) {
        springRepository.findById(id).ifPresent(jpa -> {
            jpa.setDeleted(true);
            springRepository.save(jpa);
        });
    }

    private InvoiceJpaEntity toJpaEntity(Invoice domain) {
        InvoiceJpaEntity jpa = new InvoiceJpaEntity();
        jpa.setId(domain.getId().value());
        jpa.setClinicId(domain.getClinicId());
        jpa.setPatientId(domain.getPatientId());
        jpa.setPatientName(domain.getPatientName());
        // Generate invoice number if missing
        String invNum = domain.getInvoiceNumber();
        if (invNum == null || invNum.isBlank()) {
            invNum = "INV-" + domain.getId().value().toString().substring(0, 8).toUpperCase();
        }
        jpa.setInvoiceNumber(invNum);
        jpa.setIssueDate(domain.getIssueDate() != null ? domain.getIssueDate() : LocalDate.now());
        jpa.setDueDate(domain.getDueDate());
        jpa.setSubtotal(domain.getSubtotal() != null ? domain.getSubtotal() : BigDecimal.ZERO);
        jpa.setTaxPercent(domain.getTaxPercent() != null ? domain.getTaxPercent() : BigDecimal.ZERO);
        jpa.setTaxAmount(domain.getTaxAmount() != null ? domain.getTaxAmount() : BigDecimal.ZERO);
        jpa.setTotal(domain.getTotal() != null ? domain.getTotal()
                : (domain.getAmount() != null ? BigDecimal.valueOf(domain.getAmount().getAmount()) : BigDecimal.ZERO));
        jpa.setPaidAmount(domain.getPaidAmount() != null ? domain.getPaidAmount() : BigDecimal.ZERO);
        jpa.setStatus(domain.getStatus() != null ? domain.getStatus().getValue() : "DRAFT");
        jpa.setNotes(domain.getNotes());
        return jpa;
    }

    private Invoice toDomain(InvoiceJpaEntity jpa) {
        return new Invoice(
            new InvoiceId(jpa.getId()),
            jpa.getPatientId(),
            jpa.getPatientName(),
            jpa.getInvoiceNumber(),
            new Money(jpa.getTotal() != null ? jpa.getTotal().doubleValue() : 0.0, "USD"),
            jpa.getSubtotal(),
            jpa.getTaxPercent(),
            jpa.getTaxAmount(),
            jpa.getTotal(),
            jpa.getPaidAmount(),
            new InvoiceStatus(jpa.getStatus()),
            jpa.getIssueDate(),
            jpa.getDueDate(),
            jpa.getNotes(),
            jpa.getClinicId(),
            jpa.getCreatedAt()
        );
    }
}
