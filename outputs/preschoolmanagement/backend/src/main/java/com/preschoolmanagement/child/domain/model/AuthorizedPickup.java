package com.preschoolmanagement.child.domain.model;

import com.preschoolmanagement.child.domain.valueobject.AuthorizedPickupId;
import com.preschoolmanagement.domain.shared.Entity;

public class AuthorizedPickup extends Entity<AuthorizedPickupId> {

    private final String firstName;
    private final String lastName;
    private final String relationship;
    private final String contactNumber;

    public AuthorizedPickup(AuthorizedPickupId id, String firstName, String lastName, String relationship, String contactNumber) {
        super(id);
        this.firstName = firstName;
        this.lastName = lastName;
        this.relationship = relationship;
        this.contactNumber = contactNumber;
    }

    public String getFirstName() { return this.firstName; }

    public String getLastName() { return this.lastName; }

    public String getRelationship() { return this.relationship; }

    public String getContactNumber() { return this.contactNumber; }

}
