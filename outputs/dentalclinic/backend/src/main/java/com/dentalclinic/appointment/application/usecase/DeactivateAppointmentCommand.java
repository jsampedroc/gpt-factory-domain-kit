package com.dentalclinic.appointment.application.usecase;

import java.util.UUID;

public record DeactivateAppointmentCommand(
    UUID appointmentId
) {}