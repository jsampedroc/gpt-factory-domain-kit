package com.dentalclinic.treatment.domain.valueobject;

import com.dentalclinic.domain.shared.ValueObject;
import com.dentalclinic.treatment.domain.valueobject.TreatmentId;
import java.util.Objects;
import java.util.UUID;

public final class TreatmentId implements ValueObject {
    private final UUID value;

    public TreatmentId(UUID value) {
        this.value = Objects.requireNonNull(value, "TreatmentId value cannot be null");
    }

    public UUID value() {
        return value;
    }

    public static TreatmentId newId() {
        return new TreatmentId(UUID.randomUUID());
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        TreatmentId that = (TreatmentId) o;
        return Objects.equals(value, that.value);
    }

    @Override
    public int hashCode() {
        return Objects.hash(value);
    }

    @Override
    public String toString() {
        return "TreatmentId{" +
                "value=" + value +
                '}';
    }
}
