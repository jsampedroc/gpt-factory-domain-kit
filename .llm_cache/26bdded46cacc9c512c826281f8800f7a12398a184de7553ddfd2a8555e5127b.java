package com.preschoolmanagement.child.domain.valueobject;

import com.preschoolmanagement.domain.shared.ValueObject;

import java.util.Objects;
import java.util.UUID;

public final class ImmunizationId implements ValueObject {
    private final UUID value;

    public ImmunizationId(UUID value) {
        this.value = Objects.requireNonNull(value, "ID value cannot be null");
    }

    public UUID value() {
        return value;
    }

    public static ImmunizationId newId() {
        return new ImmunizationId(UUID.randomUUID());
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        ImmunizationId that = (ImmunizationId) o;
        return Objects.equals(value, that.value);
    }

    @Override
    public int hashCode() {
        return Objects.hash(value);
    }

    @Override
    public String toString() {
        return "ImmunizationId{" +
                "value=" + value +
                '}';
    }
}