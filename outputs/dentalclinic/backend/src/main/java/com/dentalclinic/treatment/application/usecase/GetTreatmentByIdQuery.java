package com.dentalclinic.treatment.application.usecase;

import java.util.UUID;

public record GetTreatmentByIdQuery(
    UUID treatmentId
) {}