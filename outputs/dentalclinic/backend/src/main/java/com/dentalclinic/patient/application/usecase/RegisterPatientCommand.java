package com.dentalclinic.patient.application.usecase;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Past;
import jakarta.validation.constraints.Size;
import java.time.LocalDate;

public record RegisterPatientCommand(
    @NotBlank(message = "El nombre completo es obligatorio")
    @Size(max = 200, message = "El nombre completo no puede superar 200 caracteres")
    String fullName,

    @Size(max = 100, message = "El nombre no puede superar 100 caracteres")
    String firstName,

    @Size(max = 100, message = "El apellido no puede superar 100 caracteres")
    String lastName,

    @Past(message = "La fecha de nacimiento debe ser en el pasado")
    LocalDate birthDate,

    @Size(max = 20)
    String dniNie,

    @Size(max = 200)
    String email,

    @Size(max = 30)
    String phone,

    @Size(max = 20)
    String gender,

    String address,

    @Size(max = 100)
    String city,

    @Size(max = 10)
    String postalCode
) {}
