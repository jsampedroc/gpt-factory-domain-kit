package com.dentalclinic.invoice.application.usecase;

import com.dentalclinic.invoice.domain.model.Invoice;
import com.dentalclinic.invoice.domain.repository.InvoiceRepository;
import com.dentalclinic.invoice.domain.valueobject.InvoiceId;
import com.dentalclinic.shared.kernel.ClinicContext;
import java.math.BigDecimal;
import java.time.LocalDate;
import java.util.UUID;
import com.dentalclinic.invoice.domain.event.InvoiceCreatedEvent;
import org.springframework.context.ApplicationEventPublisher;
import org.springframework.cache.annotation.CacheEvict;
import org.springframework.stereotype.Service;

/**
 * Registers a new Invoice in the system
 */
@Service
public class RegisterInvoiceUseCase {

    private final InvoiceRepository repository;
    private final ApplicationEventPublisher publisher;
    private final ClinicContext clinicContext;

    public RegisterInvoiceUseCase(InvoiceRepository repository,
                                   ApplicationEventPublisher publisher,
                                   ClinicContext clinicContext) {
        this.repository = repository;
        this.publisher = publisher;
        this.clinicContext = clinicContext;
    }

    @CacheEvict(value = "dashboard", allEntries = true)
    public Invoice execute(RegisterInvoiceCommand command) {
        UUID newId = UUID.randomUUID();
        BigDecimal total = command.amount() != null
                ? BigDecimal.valueOf(command.amount().getAmount()) : BigDecimal.ZERO;

        Invoice invoice = new Invoice(
            new InvoiceId(newId),
            command.patientId(),
            null,
            null,
            command.amount(),
            total,
            BigDecimal.ZERO,
            BigDecimal.ZERO,
            total,
            BigDecimal.ZERO,
            command.status(),
            command.issueDate() != null ? command.issueDate() : LocalDate.now(),
            null,
            null,
            clinicContext.current(),
            null
        );
        publisher.publishEvent(InvoiceCreatedEvent.of(invoice.getId().value(), invoice.getPatientId()));
        return repository.save(invoice);
    }
}
