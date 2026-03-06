package com.preschoolmanagement.domain.valueobject;

import com.preschoolmanagement.domain.shared.ValueObject;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;
import java.util.Objects;

public record Allergy(
        @NotBlank(message = "Allergy value cannot be blank")
        @Size(max = 100, message = "Allergy value cannot exceed 100 characters")
        String value
) implements ValueObject {

    public Allergy {
        Objects.requireNonNull(value, "Allergy value cannot be null");
        if (value.isBlank()) {
            throw new IllegalArgumentException("Allergy value cannot be blank");
        }
        if (value.length() > 100) {
            throw new IllegalArgumentException("Allergy value cannot exceed 100 characters");
        }
    }
}