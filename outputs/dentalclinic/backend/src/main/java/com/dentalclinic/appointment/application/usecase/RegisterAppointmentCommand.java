package com.dentalclinic.appointment.application.usecase;

import jakarta.validation.constraints.FutureOrPresent;
import jakarta.validation.constraints.NotNull;
import java.time.LocalDateTime;
import java.util.UUID;

public record RegisterAppointmentCommand(
    @NotNull(message = "El paciente es obligatorio")
    UUID patientId,

    String patientName,

    UUID practitionerId,

    String practitionerName,

    @NotNull(message = "La hora de inicio es obligatoria")
    @FutureOrPresent(message = "La hora de inicio debe ser presente o futura")
    LocalDateTime startTime,

    @NotNull(message = "La hora de fin es obligatoria")
    LocalDateTime endTime,

    String procedureName,

    String notes
) {}
