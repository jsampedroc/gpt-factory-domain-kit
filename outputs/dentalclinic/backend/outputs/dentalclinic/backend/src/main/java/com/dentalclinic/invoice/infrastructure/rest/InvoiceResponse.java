package com.dentalclinic.invoice.infrastructure.rest;

import java.util.UUID;

public record InvoiceResponse(
    UUID id,
    String patientId,
    Double amount,
    String status,
    String issueDate
) {}
