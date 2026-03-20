package com.dentalclinic.appointment.application.usecase;

import java.util.UUID;

public record GetAppointmentByIdQuery(
    UUID appointmentId
) {}