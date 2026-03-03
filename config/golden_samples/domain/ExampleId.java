package com.example.domain.valueobject;

import com.example.domain.shared.ValueObject;

import java.util.Objects;
import java.util.UUID;

public final class ExampleId implements ValueObject {

    private final UUID value;

    public ExampleId(UUID value) {
        this.value = Objects.requireNonNull(value);
    }

    public UUID value() {
        return value;
    }
}