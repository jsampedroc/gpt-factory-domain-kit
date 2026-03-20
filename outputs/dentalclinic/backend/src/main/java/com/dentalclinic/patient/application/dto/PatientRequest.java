package com.dentalclinic.patient.application.dto;

import java.time.LocalDate;

public record PatientRequest(
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
        String notes
) {}
