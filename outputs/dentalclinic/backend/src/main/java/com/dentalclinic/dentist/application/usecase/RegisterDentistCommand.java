package com.dentalclinic.dentist.application.usecase;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

public record RegisterDentistCommand(
    @NotBlank(message = "El nombre es obligatorio")
    @Size(max = 100, message = "El nombre no puede superar 100 caracteres")
    String firstName,

    @NotBlank(message = "El apellido es obligatorio")
    @Size(max = 100, message = "El apellido no puede superar 100 caracteres")
    String lastName,

    @NotBlank(message = "El número de licencia es obligatorio")
    @Size(max = 50, message = "El número de licencia no puede superar 50 caracteres")
    String licenseNumber
) {}
