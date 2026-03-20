package com.dentalclinic.dentist.infrastructure.rest;

import java.util.UUID;

public record DentistResponse(
    UUID id,
    String firstName,
    String lastName,
    String licenseNumber
) {}
