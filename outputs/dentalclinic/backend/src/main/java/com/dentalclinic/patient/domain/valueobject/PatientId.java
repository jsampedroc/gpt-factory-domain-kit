package com.dentalclinic.patient.domain.valueobject;

import com.dentalclinic.domain.shared.ValueObject;
import com.dentalclinic.patient.domain.valueobject.PatientId;
import java.util.Objects;
import java.util.UUID;

public final class PatientId implements ValueObject {
    private final UUID value;

    public PatientId(UUID value) {
        this.value = Objects.requireNonNull(value, "PatientId value cannot be null");
    }

    public UUID value() {
        return value;
    }

    public static PatientId newId() {
        return new PatientId(UUID.randomUUID());
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        PatientId patientId = (PatientId) o;
        return Objects.equals(value, patientId.value);
    }

    @Override
    public int hashCode() {
        return Objects.hash(value);
    }

    @Override
    public String toString() {
        return "PatientId{" +
                "value=" + value +
                '}';
    }
}
