package com.dentalclinic.dentist.application.dto;

import java.util.UUID;

public record DentistResponse(
        UUID id,
        String firstName,
        String lastName,
        String licenseNumber,
        UUID dentistId
) {}
