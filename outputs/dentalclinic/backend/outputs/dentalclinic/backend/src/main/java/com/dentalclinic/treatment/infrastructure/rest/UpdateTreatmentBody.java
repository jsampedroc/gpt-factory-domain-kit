package com.dentalclinic.treatment.infrastructure.rest;

import java.util.UUID;

public record UpdateTreatmentBody(
    String appointmentId,
    String description,
    Double cost
) {}
