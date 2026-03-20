package com.dentalclinic.invoice.infrastructure.rest;

import java.util.UUID;

public record UpdateInvoiceBody(
    String patientId,
    Double amount,
    String status,
    String issueDate
) {}
