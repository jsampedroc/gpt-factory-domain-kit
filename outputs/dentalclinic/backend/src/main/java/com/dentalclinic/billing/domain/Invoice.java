package com.dentalclinic.billing.domain;

import com.dentalclinic.shared.kernel.BaseEntity;
import jakarta.persistence.*;
import java.math.BigDecimal;
import java.time.LocalDate;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

@Entity
@Table(name = "bill_invoice")
public class Invoice extends BaseEntity {

    @Column(name = "invoice_number", nullable = false, unique = true)
    private String invoiceNumber;

    @Column(name = "patient_id", nullable = false, columnDefinition = "uuid")
    private UUID patientId;

    @Column(name = "patient_name")
    private String patientName;

    @Column(name = "issue_date", nullable = false)
    private LocalDate issueDate;

    @Column(name = "due_date")
    private LocalDate dueDate;

    @Column(name = "subtotal", precision = 10, scale = 2, nullable = false)
    private BigDecimal subtotal = BigDecimal.ZERO;

    @Column(name = "tax_percent", precision = 5, scale = 2)
    private BigDecimal taxPercent = BigDecimal.ZERO;

    @Column(name = "tax_amount", precision = 10, scale = 2)
    private BigDecimal taxAmount = BigDecimal.ZERO;

    @Column(name = "total", precision = 10, scale = 2, nullable = false)
    private BigDecimal total = BigDecimal.ZERO;

    @Column(name = "paid_amount", precision = 10, scale = 2)
    private BigDecimal paidAmount = BigDecimal.ZERO;

    @Column(name = "status", nullable = false)
    @Enumerated(EnumType.STRING)
    private InvoiceStatus status = InvoiceStatus.DRAFT;

    @Column(name = "notes", columnDefinition = "text")
    private String notes;

    @OneToMany(cascade = CascadeType.ALL, orphanRemoval = true)
    @JoinColumn(name = "invoice_id")
    private List<InvoiceLine> lines = new ArrayList<>();

    protected Invoice() {}

    public Invoice(String invoiceNumber, UUID patientId, String patientName, LocalDate issueDate, UUID clinicId) {
        this.invoiceNumber = invoiceNumber;
        this.patientId = patientId;
        this.patientName = patientName;
        this.issueDate = issueDate;
        setClinicId(clinicId);
    }

    public String getInvoiceNumber() { return invoiceNumber; }
    public UUID getPatientId() { return patientId; }
    public String getPatientName() { return patientName; }
    public LocalDate getIssueDate() { return issueDate; }
    public LocalDate getDueDate() { return dueDate; }
    public void setDueDate(LocalDate dueDate) { this.dueDate = dueDate; }
    public BigDecimal getSubtotal() { return subtotal; }
    public void setSubtotal(BigDecimal subtotal) { this.subtotal = subtotal; }
    public BigDecimal getTaxPercent() { return taxPercent; }
    public void setTaxPercent(BigDecimal taxPercent) { this.taxPercent = taxPercent; }
    public BigDecimal getTaxAmount() { return taxAmount; }
    public void setTaxAmount(BigDecimal taxAmount) { this.taxAmount = taxAmount; }
    public BigDecimal getTotal() { return total; }
    public void setTotal(BigDecimal total) { this.total = total; }
    public BigDecimal getPaidAmount() { return paidAmount; }
    public void setPaidAmount(BigDecimal paidAmount) { this.paidAmount = paidAmount; }
    public InvoiceStatus getStatus() { return status; }
    public void setStatus(InvoiceStatus status) { this.status = status; }
    public String getNotes() { return notes; }
    public void setNotes(String notes) { this.notes = notes; }
    public List<InvoiceLine> getLines() { return lines; }
    public void issue() { this.status = InvoiceStatus.ISSUED; }
    public void cancel() { this.status = InvoiceStatus.CANCELLED; }
    public BigDecimal getOutstanding() { return total.subtract(paidAmount); }
}
