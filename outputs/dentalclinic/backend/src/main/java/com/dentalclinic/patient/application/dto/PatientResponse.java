package com.dentalclinic.patient.application.dto;

import java.time.Instant;
import java.util.List;
import java.util.UUID;

public record PatientResponse(
        UUID id,
        String fullName,
        String firstName,
        String lastName,
        String birthDate,
        String dniNie,
        String email,
        String phone,
        String gender,
        String bloodType,
        String address,
        String city,
        String postalCode,
        String notes,
        boolean active,
        List<String> clinicalAlerts,
        Instant createdAt
) {}
