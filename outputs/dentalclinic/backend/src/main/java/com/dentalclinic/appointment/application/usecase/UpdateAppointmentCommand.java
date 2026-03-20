package com.dentalclinic.appointment.application.usecase;

import jakarta.validation.constraints.NotNull;
import java.time.LocalDateTime;
import java.util.UUID;

public record UpdateAppointmentCommand(
    @NotNull(message = "El id de la cita es obligatorio")
    UUID appointmentId,

    UUID patientId,

    String patientName,

    UUID practitionerId,

    String practitionerName,

    LocalDateTime startTime,

    LocalDateTime endTime,

    String procedureName,

    String status,

    String notes
) {}
