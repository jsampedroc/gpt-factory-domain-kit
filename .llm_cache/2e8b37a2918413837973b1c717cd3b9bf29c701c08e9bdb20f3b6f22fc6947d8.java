package com.preschoolmanagement.child.domain.valueobject;

import com.preschoolmanagement.child.domain.enums.AllergySeverity;
import com.preschoolmanagement.domain.shared.ValueObject;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import java.util.Objects;

public record Allergy(
        @NotBlank String name,
        @NotNull AllergySeverity severity
) implements ValueObject {

    public Allergy {
        Objects.requireNonNull(name, "Allergy name cannot be null");
        Objects.requireNonNull(severity, "Allergy severity cannot be null");
        if (name.isBlank()) {
            throw new IllegalArgumentException("Allergy name cannot be blank");
        }
    }
}