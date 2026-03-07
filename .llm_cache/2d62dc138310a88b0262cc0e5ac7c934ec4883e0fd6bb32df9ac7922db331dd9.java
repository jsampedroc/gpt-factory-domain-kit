package com.preschoolmanagement.domain.valueobject;

import com.preschoolmanagement.domain.shared.ValueObject;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.PastOrPresent;
import java.time.LocalDate;
import java.util.Objects;

public final class Immunization implements ValueObject {

    @NotBlank
    private final String name;

    @NotNull
    @PastOrPresent
    private final LocalDate dateAdministered;

    public Immunization(String name, LocalDate dateAdministered) {
        this.name = Objects.requireNonNull(name, "Immunization name must not be null");
        this.dateAdministered = Objects.requireNonNull(dateAdministered, "Immunization date administered must not be null");

        if (this.name.isBlank()) {
            throw new IllegalArgumentException("Immunization name must not be blank");
        }
    }

    public String name() {
        return name;
    }

    public LocalDate dateAdministered() {
        return dateAdministered;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        Immunization that = (Immunization) o;
        return Objects.equals(name, that.name) && Objects.equals(dateAdministered, that.dateAdministered);
    }

    @Override
    public int hashCode() {
        return Objects.hash(name, dateAdministered);
    }

    @Override
    public String toString() {
        return "Immunization[" +
                "name=" + name +
                ", dateAdministered=" + dateAdministered +
                ']';
    }
}