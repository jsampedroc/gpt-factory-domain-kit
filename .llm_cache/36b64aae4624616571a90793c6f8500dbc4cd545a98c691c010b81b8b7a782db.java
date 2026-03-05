package com.preschoolmanagement.domain.valueobject;

import com.preschoolmanagement.domain.shared.ValueObject;

import java.util.Objects;
import java.util.UUID;

public record EmergencyContactId(UUID value) implements ValueObject {
    public EmergencyContactId {
        Objects.requireNonNull(value, "value must not be null");
    }

    public static EmergencyContactId newId() {
        return new EmergencyContactId(UUID.randomUUID());
    }
}