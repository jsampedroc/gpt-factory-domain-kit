package com.dentalclinic.treatment.application.usecase;

import com.dentalclinic.domain.valueobject.Money;
import jakarta.validation.Valid;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;
import java.util.UUID;

public record UpdateTreatmentCommand(
    @NotNull(message = "El id del tratamiento es obligatorio")
    UUID treatmentId,

    @NotNull(message = "La cita es obligatoria")
    UUID appointmentId,

    @NotBlank(message = "La descripción es obligatoria")
    @Size(max = 500, message = "La descripción no puede superar 500 caracteres")
    String description,

    @NotNull(message = "El coste es obligatorio")
    @Valid
    Money cost
) {}
