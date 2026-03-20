package com.dentalclinic.patient.application.usecase;

import java.util.UUID;

public record DeactivatePatientCommand(
    UUID patientId
) {}