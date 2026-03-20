package com.dentalclinic.patient.api;

import jakarta.validation.constraints.NotBlank;
import java.time.LocalDate;

public record CreatePatientRequest(
    @NotBlank String fullName,
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
    String notes
) {}
