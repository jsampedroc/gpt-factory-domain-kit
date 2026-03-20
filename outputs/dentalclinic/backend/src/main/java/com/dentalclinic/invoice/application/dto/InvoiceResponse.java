package com.dentalclinic.invoice.application.dto;

import java.util.UUID;

public record InvoiceResponse(
        UUID id,
        UUID invoiceId,
        UUID patientId,
        Double amount,
        String status,
        String issueDate
) {}
