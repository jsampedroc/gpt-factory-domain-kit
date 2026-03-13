package com.preschoolmanagement.child.domain.model;

import com.preschoolmanagement.child.domain.valueobject.AuthorizedPickupId;
import com.preschoolmanagement.domain.shared.Entity;

public class AuthorizedPickup extends Entity<AuthorizedPickupId> {

    private final String firstName;
    private final String lastName;
    private final String relationshipToChild;

    public AuthorizedPickup(AuthorizedPickupId id, String firstName, String lastName, String relationshipToChild) {
        super(id);
        this.firstName = firstName;
        this.lastName = lastName;
        this.relationshipToChild = relationshipToChild;
    }

    public String getFirstName() { return this.firstName; }

    public String getLastName() { return this.lastName; }

    public String getRelationshipToChild() { return this.relationshipToChild; }

}
