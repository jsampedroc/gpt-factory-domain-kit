package com.preschoolmanagement.child.domain.valueobject;

import com.preschoolmanagement.domain.shared.ValueObject;

import java.util.Objects;
import java.util.UUID;

public final class AuthorizedPickupId implements ValueObject {
    private final UUID value;

    public AuthorizedPickupId(UUID value) {
        this.value = Objects.requireNonNull(value, "value cannot be null");
    }

    public UUID value() {
        return value;
    }

    public static AuthorizedPickupId newId() {
        return new AuthorizedPickupId(UUID.randomUUID());
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