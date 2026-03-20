package com.dentalclinic.patient.api;

import java.time.LocalDate;
import java.time.Instant;
import java.util.List;
import java.util.UUID;

public record PatientDto(
    UUID id,
    UUID clinicId,
    String fullName,
    String firstName,
    String lastName,
    LocalDate birthDate,
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
    Instant createdAt,
    Instant updatedAt
) {}
