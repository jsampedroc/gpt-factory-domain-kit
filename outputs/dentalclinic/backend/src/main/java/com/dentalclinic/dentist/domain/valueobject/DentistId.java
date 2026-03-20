package com.dentalclinic.dentist.domain.valueobject;

import com.dentalclinic.dentist.domain.valueobject.DentistId;
import com.dentalclinic.domain.shared.ValueObject;
import java.util.Objects;
import java.util.UUID;

public final class DentistId implements ValueObject {
    private final UUID value;

    public DentistId(UUID value) {
        this.value = Objects.requireNonNull(value, "DentistId value cannot be null");
    }

    public UUID value() {
        return value;
    }

    public static DentistId newId() {
        return new DentistId(UUID.randomUUID());
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        DentistId dentistId = (DentistId) o;
        return Objects.equals(value, dentistId.value);
    }

    @Override
    public int hashCode() {
        return Objects.hash(value);
    }

    @Override
    public String toString() {
        return "DentistId{" +
                "value=" + value +
                '}';
    }
}
