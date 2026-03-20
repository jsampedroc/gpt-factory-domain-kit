package com.dentalclinic.invoice.application.usecase;

import java.util.UUID;

public record GetInvoiceByIdQuery(
    UUID invoiceId
) {}