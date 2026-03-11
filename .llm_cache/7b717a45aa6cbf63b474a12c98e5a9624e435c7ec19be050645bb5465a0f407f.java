package com.preschoolmanagement.child.domain.valueobject;

import com.preschoolmanagement.domain.shared.ValueObject;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;
import java.util.Objects;

public final class AllergySeverity implements ValueObject {
    private final String value;

    public AllergySeverity(String value) {
        this.value = Objects.requireNonNull(value, "AllergySeverity value cannot be null");
        validate(value);
    }

    private void validate(String value) {
        if (value.isBlank()) {
            throw new IllegalArgumentException("AllergySeverity value cannot be blank");
        }
        if (value.length() > 50) {
            throw new IllegalArgumentException("AllergySeverity value cannot exceed 50 characters");
        }
    }

    public String getValue() {
        return value;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        AllergySeverity that = (AllergySeverity) o;
        return Objects.equals(value, that.value);
    }

    @Override
    public int hashCode() {
        return Objects.hash(value);
    }

    @Override
    public String toString() {
        return "AllergySeverity{" +
                "value='" + value + '\'' +
                '}';
    }
}