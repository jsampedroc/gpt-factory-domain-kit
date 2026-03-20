package com.dentalclinic.dentist.infrastructure.rest;

import java.util.UUID;

public record UpdateDentistBody(
    String firstName,
    String lastName,
    String licenseNumber
) {}
