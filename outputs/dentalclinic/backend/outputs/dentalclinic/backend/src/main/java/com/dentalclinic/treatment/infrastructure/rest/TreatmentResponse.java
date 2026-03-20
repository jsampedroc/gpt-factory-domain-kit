package com.dentalclinic.treatment.infrastructure.rest;

import java.util.UUID;

public record TreatmentResponse(
    UUID id,
    String appointmentId,
    String description,
    Double cost
) {}
