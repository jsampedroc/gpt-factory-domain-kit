package com.preschoolmanagement.domain.valueobject;

import com.preschoolmanagement.domain.shared.ValueObject;
import com.preschoolmanagement.domain.shared.AllergySeverity;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import java.util.Objects;

public final class Allergy implements ValueObject {

    @NotBlank
    private final String allergen;

    @NotNull
    private final AllergySeverity severity;

    public Allergy(String allergen, AllergySeverity severity) {
        this.allergen = Objects.requireNonNull(allergen, "Allergen cannot be null");
        this.severity = Objects.requireNonNull(severity, "Severity cannot be null");

        if (this.allergen.isBlank()) {
            throw new IllegalArgumentException("Allergen cannot be blank");
        }
    }

    public String allergen() {
        return allergen;
    }

    public AllergySeverity severity() {
        return severity;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        Allergy allergy = (Allergy) o;
        return Objects.equals(allergen, allergy.allergen) && severity == allergy.severity;
    }

    @Override
    public int hashCode() {
        return Objects.hash(allergen, severity);
    }

    @Override
    public String toString() {
        return "Allergy{" +
                "allergen='" + allergen + '\'' +
                ", severity=" + severity +
                '}';
    }
}