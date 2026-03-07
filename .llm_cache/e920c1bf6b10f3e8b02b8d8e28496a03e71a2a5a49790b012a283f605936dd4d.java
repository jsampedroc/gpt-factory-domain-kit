package com.preschoolmanagement.child.shared.application.dto;

public class AuthorizedPickupResponse {

    private final String firstName;
    private final String lastName;
    private final String contactNumber;
    private final String relationship;

    public AuthorizedPickupResponse(String firstName, String lastName, String contactNumber, String relationship) {
        this.firstName = firstName;
        this.lastName = lastName;
        this.contactNumber = contactNumber;
        this.relationship = relationship;
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

    public String relationship() {
        return relationship;
    }
}