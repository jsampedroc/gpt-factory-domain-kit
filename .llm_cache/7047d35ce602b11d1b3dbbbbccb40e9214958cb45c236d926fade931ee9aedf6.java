package com.preschoolmanagement.domain.model;

import com.preschoolmanagement.domain.shared.Entity;
import com.preschoolmanagement.domain.valueobject.ParentId;

import java.util.Objects;

public class Parent extends Entity<ParentId> {

    private final String firstName;
    private final String lastName;
    private final String contactNumber;

    public Parent(
            ParentId id,
            String firstName,
            String lastName,
            String contactNumber
    ) {
        super(id);
        this.firstName = Objects.requireNonNull(firstName);
        this.lastName = Objects.requireNonNull(lastName);
        this.contactNumber = Objects.requireNonNull(contactNumber);
    }

    public String firstName() {
        return firstName;
    }

    public String lastName() {
        return lastName;
    }

    public String contactNumber() {
        return contactNumber;
    }
}