package com.preschoolmanagement.domain.valueobject;

import com.preschoolmanagement.domain.shared.ValueObject;

import java.util.Objects;
import java.util.UUID;

public final class AuthorizedPickupId implements ValueObject {
    private final UUID value;

    public AuthorizedPickupId(UUID value) {
        this.value = Objects.requireNonNull(value, "ID value cannot be null");
    }

    public static AuthorizedPickupId newId() {
        return new AuthorizedPickupId(UUID.randomUUID());
    }

    public UUID value() {
        return value;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        AuthorizedPickupId that = (AuthorizedPickupId) o;
        return Objects.equals(value, that.value);
    }

    @Override
    public int hashCode() {
        return Objects.hash(value);
    }

    @Override
    public String toString() {
        return "AuthorizedPickupId{" +
                "value=" + value +
                '}';
    }
}