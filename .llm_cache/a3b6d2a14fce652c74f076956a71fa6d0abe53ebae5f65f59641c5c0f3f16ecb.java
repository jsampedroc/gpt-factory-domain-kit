package com.preschoolmanagement.domain.valueobject;

import com.preschoolmanagement.domain.shared.ValueObject;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import java.time.LocalDate;
import java.util.Objects;

public final class ImmunizationRecord implements ValueObject {
    @NotBlank
    private final String vaccineName;
    @NotNull
    private final LocalDate dateAdministered;

    public ImmunizationRecord(String vaccineName, LocalDate dateAdministered) {
        this.vaccineName = Objects.requireNonNull(vaccineName, "vaccineName must not be null");
        this.dateAdministered = Objects.requireNonNull(dateAdministered, "dateAdministered must not be null");
        
        if (vaccineName.isBlank()) {
            throw new IllegalArgumentException("vaccineName must not be blank");
        }
    }

    public String vaccineName() {
        return vaccineName;
    }

    public LocalDate dateAdministered() {
        return dateAdministered;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        ImmunizationRecord that = (ImmunizationRecord) o;
        return Objects.equals(vaccineName, that.vaccineName) && Objects.equals(dateAdministered, that.dateAdministered);
    }

    @Override
    public int hashCode() {
        return Objects.hash(vaccineName, dateAdministered);
    }

    @Override
    public String toString() {
        return "ImmunizationRecord[" +
                "vaccineName=" + vaccineName + ", " +
                "dateAdministered=" + dateAdministered + ']';
    }
}