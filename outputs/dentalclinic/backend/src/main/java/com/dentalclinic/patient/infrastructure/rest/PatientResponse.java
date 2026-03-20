package com.dentalclinic.patient.infrastructure.rest;

import java.util.UUID;

public record PatientResponse(
    UUID id,
    String firstName,
    String lastName,
    String birthDate
) {}
