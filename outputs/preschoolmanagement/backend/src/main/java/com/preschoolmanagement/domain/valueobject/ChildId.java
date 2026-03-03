package com.preschoolmanagement.domain.valueobject;

import com.preschoolmanagement.domain.shared.ValueObject;

import java.util.Objects;
import java.util.UUID;

public final class ChildId implements ValueObject {

    private final UUID value;

    public ChildId(UUID value) {
        this.value = Objects.requireNonNull(value);
    }

    public UUID value() {
        return value;
    }
}
