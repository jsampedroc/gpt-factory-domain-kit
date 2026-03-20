package com.dentalclinic.treatment.application.dto;

import com.dentalclinic.domain.valueobject.Money;
import java.util.UUID;

public record TreatmentRequest(
        UUID treatmentId,
        UUID appointmentId,
        String description,
        Money cost
) {}
