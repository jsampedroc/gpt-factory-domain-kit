package com.dentalclinic.appointment.application.dto;

import java.time.Instant;
import java.util.UUID;

public record AppointmentResponse(
        UUID id,
        UUID patientId,
        String patientName,
        UUID practitionerId,
        String practitionerName,
        String startTime,
        String endTime,
        String procedureName,
        String status,
        String notes,
        UUID clinicId,
        Instant createdAt
) {}
