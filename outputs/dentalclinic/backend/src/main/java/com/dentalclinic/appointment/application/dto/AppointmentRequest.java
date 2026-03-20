package com.dentalclinic.appointment.application.dto;

import com.dentalclinic.appointment.domain.valueobject.AppointmentStatus;
import java.time.LocalDateTime;
import java.util.UUID;

public record AppointmentRequest(
        UUID appointmentId,
        UUID patientId,
        UUID dentistId,
        LocalDateTime appointmentDate,
        AppointmentStatus status
) {}
