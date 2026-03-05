package com.preschoolmanagement.domain.valueobject;

import com.preschoolmanagement.domain.shared.ValueObject;

import java.util.Objects;
import java.util.UUID;

public record ChildId(UUID value) implements ValueObject {
    public ChildId {
        Objects.requireNonNull(value, "ChildId value cannot be null");
    }

    public static ChildId newId() {
        return new ChildId(UUID.randomUUID());
    }
}