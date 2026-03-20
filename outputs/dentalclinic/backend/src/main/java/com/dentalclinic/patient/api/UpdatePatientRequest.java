package com.dentalclinic.patient.api;

import java.time.LocalDate;
import java.util.List;

public record UpdatePatientRequest(
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
    List<String> clinicalAlerts
) {}
