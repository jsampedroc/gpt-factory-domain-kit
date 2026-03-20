package com.dentalclinic.dentist.application.dto;

import java.util.UUID;

public record DentistRequest(
        String firstName,
        String lastName,
        String licenseNumber,
        UUID dentistId
) {}
