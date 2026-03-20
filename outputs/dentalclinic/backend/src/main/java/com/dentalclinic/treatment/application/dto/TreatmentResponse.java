package com.dentalclinic.treatment.application.dto;

import java.util.UUID;

public record TreatmentResponse(
        UUID id,
        UUID treatmentId,
        UUID appointmentId,
        String description,
        Double cost
) {}
