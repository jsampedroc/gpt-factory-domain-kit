package com.preschoolmanagement.domain.valueobject;

import com.preschoolmanagement.domain.shared.ValueObject;

import java.util.Objects;
import java.util.UUID;

public final class ParentId implements ValueObject {
    private final UUID value;

    private ParentId(UUID value) {
        this.value = Objects.requireNonNull(value, "ID value cannot be null");
    }

    public static ParentId newId() {
        return new ParentId(UUID.randomUUID());
    }

    public static ParentId from(UUID value) {
        return new ParentId(value);
    }

    public UUID value() {
        return value;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        ParentId parentId = (ParentId) o;
        return Objects.equals(value, parentId.value);
    }

    @Override
    public int hashCode() {
        return Objects.hash(value);
    }

    @Override
    public String toString() {
        return "ParentId{" +
                "value=" + value +
                '}';
    }
}