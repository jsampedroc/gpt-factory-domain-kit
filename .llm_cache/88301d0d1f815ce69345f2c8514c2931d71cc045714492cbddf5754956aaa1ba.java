package com.preschoolmanagement.child.application.dto;

import jakarta.validation.constraints.NotBlank;

public class AuthorizedPickupRequest {

    private String firstName;

    private String lastName;

    private String relationship;

    @NotBlank
    private String contactNumber;

    public AuthorizedPickupRequest() {
    }

    public AuthorizedPickupRequest(String firstName, String lastName, String relationship, String contactNumber) {
        this.firstName = firstName;
        this.lastName = lastName;
        this.relationship = relationship;
        this.contactNumber = contactNumber;
    }

    public String firstName() {
        return firstName;
    }

    public String lastName() {
        return lastName;
    }

    public String relationship() {
        return relationship;
    }

    public String contactNumber() {
        return contactNumber;
    }
}