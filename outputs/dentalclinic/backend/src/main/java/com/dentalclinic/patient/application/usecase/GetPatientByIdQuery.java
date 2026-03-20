package com.dentalclinic.patient.application.usecase;

import java.util.UUID;

public record GetPatientByIdQuery(
    UUID patientId
) {}