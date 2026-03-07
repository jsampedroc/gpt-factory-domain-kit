package com.preschoolmanagement.child.domain.valueobject;

import com.preschoolmanagement.domain.shared.ValueObject;

import java.util.Objects;
import java.util.UUID;

public final class AllergyId implements ValueObject {
    private final UUID value;

    public AllergyId(UUID value) {
        this.value = Objects.requireNonNull(value, "ID value cannot be null");
    }

    public UUID value() {
        return value;
    }

    public static AllergyId newId() {
        return new AllergyId(UUID.randomUUID());
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        AllergyId allergyId = (AllergyId) o;
        return Objects.equals(value, allergyId.value);
    }

    @Override
    public int hashCode() {
        return Objects.hash(value);
    }

    @Override
    public String toString() {
        return "AllergyId{" +
                "value=" + value +
                '}';
    }
}