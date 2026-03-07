package com.preschoolmanagement.domain.valueobject;

import com.preschoolmanagement.domain.shared.ValueObject;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;
import java.util.Objects;

public record Immunization(
        @NotBlank(message = "Immunization value cannot be blank")
        @Size(max = 255, message = "Immunization value must not exceed 255 characters")
        String value
) implements ValueObject {

    public Immunization {
        Objects.requireNonNull(value, "Immunization value cannot be null");
        if (value.isBlank()) {
            throw new IllegalArgumentException("Immunization value cannot be blank");
        }
        if (value.length() > 255) {
            throw new IllegalArgumentException("Immunization value must not exceed 255 characters");
        }
    }
}