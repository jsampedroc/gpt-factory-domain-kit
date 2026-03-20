package com.dentalclinic.appointment.domain.valueobject;

import com.dentalclinic.appointment.domain.valueobject.AppointmentId;
import com.dentalclinic.domain.shared.ValueObject;
import java.util.Objects;
import java.util.UUID;

public final class AppointmentId implements ValueObject {
    private final UUID value;

    public AppointmentId(UUID value) {
        this.value = Objects.requireNonNull(value, "ID value cannot be null");
    }

    public UUID value() {
        return value;
    }

    public static AppointmentId newId() {
        return new AppointmentId(UUID.randomUUID());
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        AppointmentId that = (AppointmentId) o;
        return Objects.equals(value, that.value);
    }

    @Override
    public int hashCode() {
        return Objects.hash(value);
    }

    @Override
    public String toString() {
        return "AppointmentId{" +
                "value=" + value +
                '}';
    }
}
