package com.dentalclinic.invoice.domain.model;

import com.dentalclinic.domain.shared.Entity;
import com.dentalclinic.invoice.domain.valueobject.InvoiceStatus;
import com.dentalclinic.invoice.domain.valueobject.InvoiceId;
import com.dentalclinic.domain.valueobject.Money;
import java.math.BigDecimal;
import java.time.Instant;
import java.time.LocalDate;
import java.util.UUID;

public class Invoice extends Entity<InvoiceId> {

    private final String invoiceNumber;
    private final UUID patientId;
    private final String patientName;
    private final Money amount;
    private final BigDecimal subtotal;
    private final BigDecimal taxPercent;
    private final BigDecimal taxAmount;
    private final BigDecimal total;
    private final BigDecimal paidAmount;
    private final InvoiceStatus status;
    private final LocalDate issueDate;
    private final LocalDate dueDate;
    private final String notes;
    private final UUID clinicId;
    private final Instant createdAt;

    public Invoice(InvoiceId id, UUID patientId, String patientName,
                   String invoiceNumber, Money amount,
                   BigDecimal subtotal, BigDecimal taxPercent, BigDecimal taxAmount,
                   BigDecimal total, BigDecimal paidAmount,
                   InvoiceStatus status, LocalDate issueDate, LocalDate dueDate,
                   String notes, UUID clinicId, Instant createdAt) {
        super(id);
        this.invoiceNumber = invoiceNumber;
        this.patientId = patientId;
        this.patientName = patientName;
        this.amount = amount;
        this.subtotal = subtotal;
        this.taxPercent = taxPercent;
        this.taxAmount = taxAmount;
        this.total = total;
        this.paidAmount = paidAmount;
        this.status = status;
        this.issueDate = issueDate;
        this.dueDate = dueDate;
        this.notes = notes;
        this.clinicId = clinicId;
        this.createdAt = createdAt;
    }

    // Legacy compat constructor
    public Invoice(InvoiceId id, UUID invoiceId, UUID patientId, Money amount,
                   InvoiceStatus status, LocalDate issueDate) {
        this(id, patientId, null, invoiceId != null ? invoiceId.toString() : null,
             amount, BigDecimal.ZERO, BigDecimal.ZERO, BigDecimal.ZERO,
             amount != null ? BigDecimal.valueOf(amount.getAmount()) : BigDecimal.ZERO,
             BigDecimal.ZERO, status, issueDate, null, null, null, null);
    }

    public String getInvoiceNumber() { return invoiceNumber; }
    public UUID getPatientId() { return patientId; }
    public String getPatientName() { return patientName; }
    public Money getAmount() { return amount; }
    public BigDecimal getSubtotal() { return subtotal; }
    public BigDecimal getTaxPercent() { return taxPercent; }
    public BigDecimal getTaxAmount() { return taxAmount; }
    public BigDecimal getTotal() { return total; }
    public BigDecimal getPaidAmount() { return paidAmount; }
    public InvoiceStatus getStatus() { return status; }
    public LocalDate getIssueDate() { return issueDate; }
    public LocalDate getDueDate() { return dueDate; }
    public String getNotes() { return notes; }
    public UUID getClinicId() { return clinicId; }
    public Instant getCreatedAt() { return createdAt; }

    // Legacy compat
    public UUID getInvoiceId() { return getId().value(); }
}
