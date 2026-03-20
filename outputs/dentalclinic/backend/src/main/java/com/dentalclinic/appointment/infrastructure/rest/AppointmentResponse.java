package com.dentalclinic.appointment.infrastructure.rest;

import java.util.UUID;

public record AppointmentResponse(
    UUID id,
    String patientId,
    String dentistId,
    String appointmentDate,
    String status
) {}
