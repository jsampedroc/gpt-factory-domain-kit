package com.preschoolmanagement.domain.valueobject;

import com.preschoolmanagement.domain.shared.ValueObject;

import java.util.Objects;
import java.util.UUID;

public final class InvoiceId implements ValueObject {

    private final UUID value;

    public InvoiceId(UUID value) {
        this.value = Objects.requireNonNull(value);
    }

    public UUID value() {
        return value;
    }
}
