package com.dentalclinic.billing;

import java.math.BigDecimal;
import java.util.UUID;

public final class BillingEvents {
    public record InvoiceIssued(UUID invoiceId, UUID patientId, UUID clinicId, String invoiceNumber, BigDecimal total) {}
    public record InvoiceCancelled(UUID invoiceId, UUID clinicId, String invoiceNumber) {}
    public record PaymentReceived(UUID invoiceId, UUID patientId, UUID clinicId, BigDecimal amount) {}
    private BillingEvents() {}
}
