package com.preschoolmanagement.child.shared.application.dto;

import jakarta.validation.constraints.NotBlank;

public class AuthorizedPickupRequest {

    private String firstName;
    private String lastName;
    private String contactNumber;
    private String relationship;

    public AuthorizedPickupRequest() {
    }

    public AuthorizedPickupRequest(String firstName, String lastName, String contactNumber, String relationship) {
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