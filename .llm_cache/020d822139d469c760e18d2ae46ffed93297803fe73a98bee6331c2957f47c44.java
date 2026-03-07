package com.preschoolmanagement.child.shared.application.dto;

import jakarta.validation.constraints.NotBlank;

public class AuthorizedPickupRequest {

    private String firstName;

    private String lastName;

    private String relationshipToChild;

    private String contactNumber;

    public AuthorizedPickupRequest() {
    }

    public AuthorizedPickupRequest(String firstName, String lastName, String relationshipToChild, String contactNumber) {
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