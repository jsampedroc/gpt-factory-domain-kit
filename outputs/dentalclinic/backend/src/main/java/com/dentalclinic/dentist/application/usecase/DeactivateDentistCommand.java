package com.dentalclinic.dentist.application.usecase;

import java.util.UUID;

public record DeactivateDentistCommand(
    UUID dentistId
) {}