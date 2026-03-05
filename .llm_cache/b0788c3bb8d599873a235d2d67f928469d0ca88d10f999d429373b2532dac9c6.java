package com.preschoolmanagement.domain.model;

import com.preschoolmanagement.domain.shared.Entity;
import com.preschoolmanagement.domain.valueobject.ChildId;

import java.time.LocalDate;
import java.util.List;
import java.util.Objects;

public class Child extends Entity<ChildId> {

    private final String firstName;
    private final String lastName;
    private final LocalDate birthDate;
    private final List<ImmunizationRecord> immunizationRecords;
    private final List<Allergy> severeAllergies;

    public Child(
            ChildId id,
            String firstName,
            String lastName,
            LocalDate birthDate,
            List<ImmunizationRecord> immunizationRecords,
            List<Allergy> severeAllergies
    ) {
        super(id);
        this.firstName = Objects.requireNonNull(firstName);
        this.lastName = Objects.requireNonNull(lastName);
        this.birthDate = Objects.requireNonNull(birthDate);
        this.immunizationRecords = Objects.requireNonNull(immunizationRecords);
        this.severeAllergies = Objects.requireNonNull(severeAllergies);
    }

    public String firstName() {
        return firstName;
    }

    public String lastName() {
        return lastName;
    }

    public LocalDate birthDate() {
        return birthDate;
    }

    public List<ImmunizationRecord> immunizationRecords() {
        return immunizationRecords;
    }

    public List<Allergy> severeAllergies() {
        return severeAllergies;
    }
}