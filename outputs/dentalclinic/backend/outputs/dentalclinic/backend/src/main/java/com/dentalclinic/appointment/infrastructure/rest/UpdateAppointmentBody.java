package com.dentalclinic.appointment.infrastructure.rest;

import java.util.UUID;

public record UpdateAppointmentBody(
    String patientId,
    String dentistId,
    String appointmentDate,
    String status
) {}
