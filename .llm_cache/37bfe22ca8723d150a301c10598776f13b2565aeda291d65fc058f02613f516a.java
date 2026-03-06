package com.preschoolmanagement.child.domain.valueobject;

import com.preschoolmanagement.domain.shared.ValueObject;

import java.util.Objects;
import java.util.UUID;

public final class ChildId implements ValueObject {
    private final UUID value;

    public ChildId(UUID value) {
        this.value = Objects.requireNonNull(value, "ChildId value cannot be null");
    }

    public UUID value() {
        return value;
    }

    public static ChildId newId() {
        return new ChildId(UUID.randomUUID());
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        ChildId childId = (ChildId) o;
        return Objects.equals(value, childId.value);
    }

    @Override
    public int hashCode() {
        return Objects.hash(value);
    }

    @Override
    public String toString() {
        return "ChildId{" +
                "value=" + value +
                '}';
    }
}