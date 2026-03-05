package com.preschoolmanagement.domain.valueobject;

import com.preschoolmanagement.domain.shared.ValueObject;

import java.util.Objects;
import java.util.UUID;

public record ParentId(UUID value) implements ValueObject {
    public ParentId {
        Objects.requireNonNull(value, "ParentId value cannot be null");
    }

    public static ParentId newId() {
        return new ParentId(UUID.randomUUID());
    }
}