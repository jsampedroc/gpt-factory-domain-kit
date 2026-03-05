package com.preschoolmanagement.domain.model;

import com.preschoolmanagement.domain.shared.Entity;
import com.preschoolmanagement.domain.valueobject.EmergencyContactId;
import com.preschoolmanagement.domain.shared.GeoLocation;

import java.util.Objects;

public class EmergencyContact extends Entity<EmergencyContactId> {

    private final String firstName;
    private final String lastName;
    private final GeoLocation relationship;
    private final String contactNumber;

    public EmergencyContact(
            EmergencyContactId id,
            String firstName,
            String lastName,
            GeoLocation relationship,
            String contactNumber
    ) {
        super(id);
        this.firstName = Objects.requireNonNull(firstName);
        this.lastName = Objects.requireNonNull(lastName);
        this.relationship = Objects.requireNonNull(relationship);
        this.contactNumber = Objects.requireNonNull(contactNumber);
    }

    public String firstName() {
        return firstName;
    }

    public String lastName() {
        return lastName;
    }

    public GeoLocation relationship() {
        return relationship;
    }

    public String contactNumber() {
        return contactNumber;
    }
}