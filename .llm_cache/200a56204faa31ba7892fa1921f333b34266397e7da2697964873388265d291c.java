package com.preschoolmanagement.domain.valueobject;

import com.preschoolmanagement.domain.shared.ValueObject;
import jakarta.validation.constraints.NotNull;
import java.util.Objects;

public final class Allergy implements ValueObject {
    private final String name;
    private final AllergySeverity severity;

    public Allergy(@NotNull String name, @NotNull AllergySeverity severity) {
        this.name = Objects.requireNonNull(name, "Allergy name must not be null");
        this.severity = Objects.requireNonNull(severity, "Allergy severity must not be null");
        validateInvariants();
    }

    private void validateInvariants() {
        if (name.isBlank()) {
            throw new IllegalArgumentException("Allergy name must not be blank");
        }
    }

    public String name() {
        return name;
    }

    public AllergySeverity severity() {
        return severity;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        Allergy allergy = (Allergy) o;
        return Objects.equals(name, allergy.name) && severity == allergy.severity;
    }

    @Override
    public int hashCode() {
        return Objects.hash(name, severity);
    }

    @Override
    public String toString() {
        return "Allergy{" +
                "name='" + name + '\'' +
                ", severity=" + severity +
                '}';
    }
}