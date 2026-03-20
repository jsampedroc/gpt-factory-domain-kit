package com.dentalclinic.invoice.application.dto;

import com.dentalclinic.domain.valueobject.Money;
import com.dentalclinic.invoice.domain.valueobject.InvoiceStatus;
import java.time.LocalDate;
import java.util.UUID;

public record InvoiceRequest(
        UUID invoiceId,
        UUID patientId,
        Money amount,
        InvoiceStatus status,
        LocalDate issueDate
) {}
