package com.dentalclinic.patient.infrastructure.rest;

import java.util.UUID;

public record UpdatePatientBody(
    String firstName,
    String lastName,
    String birthDate
) {}
