package com.dentalclinic.invoice.application.usecase;

import com.dentalclinic.domain.valueobject.Money;
import com.dentalclinic.invoice.domain.valueobject.InvoiceStatus;
import jakarta.validation.Valid;
import jakarta.validation.constraints.NotNull;
import java.time.LocalDate;
import java.util.UUID;

public record RegisterInvoiceCommand(
    @NotNull(message = "El paciente es obligatorio")
    UUID patientId,

    @NotNull(message = "El importe es obligatorio")
    @Valid
    Money amount,

    @NotNull(message = "El estado es obligatorio")
    InvoiceStatus status,

    @NotNull(message = "La fecha de emisión es obligatoria")
    LocalDate issueDate
) {}
