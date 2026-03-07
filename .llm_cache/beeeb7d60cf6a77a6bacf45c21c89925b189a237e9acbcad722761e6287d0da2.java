package com.preschoolmanagement.child.shared.application.dto;

public class AuthorizedPickupResponse {

    private final String firstName;
    private final String lastName;
    private final String relationshipToChild;
    private final String contactNumber;

    public AuthorizedPickupResponse(
            String firstName,
            String lastName,
            String relationshipToChild,
            String contactNumber
    ) {
        this.firstName = firstName;
        this.lastName = lastName;
        this.relationshipToChild = relationshipToChild;
        this.contactNumber = contactNumber;
    }

    public String firstName() {
        return firstName;
    }

    public String lastName() {
        return lastName;
    }

    public String relationshipToChild() {
        return relationshipToChild;
    }

    public String contactNumber() {
        return contactNumber;
    }
}