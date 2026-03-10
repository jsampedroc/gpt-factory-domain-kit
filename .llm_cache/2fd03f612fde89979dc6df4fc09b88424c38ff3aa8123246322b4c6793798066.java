package com.preschoolmanagement.child.domain.valueobject;

import com.preschoolmanagement.domain.shared.ValueObject;
import jakarta.validation.constraints.NotNull;
import java.util.Objects;

public final class GeoLocation implements ValueObject {
    private final Double value;

    public GeoLocation(@NotNull Double value) {
        this.value = Objects.requireNonNull(value, "GeoLocation value cannot be null");
        validateValue(this.value);
    }

    private void validateValue(Double value) {
        // Example validation: latitude/longitude ranges could be added here.
        // For now, we just ensure it's not null.
        // If specific range validation is needed, add it here.
        // e.g., if (value < -90.0 || value > 90.0) throw new IllegalArgumentException(...);
    }

    public Double value() {
        return value;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        GeoLocation that = (GeoLocation) o;
        return Objects.equals(value, that.value);
    }

    @Override
    public int hashCode() {
        return Objects.hash(value);
    }

    @Override
    public String toString() {
        return "GeoLocation{" +
                "value=" + value +
                '}';
    }
}