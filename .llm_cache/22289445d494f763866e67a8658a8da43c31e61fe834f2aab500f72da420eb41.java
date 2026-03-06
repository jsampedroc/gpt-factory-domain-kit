package com.preschoolmanagement.child.application.dto;

import jakarta.validation.constraints.NotBlank;

public class AuthorizedPickupRequest {

    private String firstName;

    private String lastName;

    private String contactNumber;

    private GeoLocation relationToChild;

    public AuthorizedPickupRequest() {
    }

    public AuthorizedPickupRequest(String firstName, String lastName, String contactNumber, GeoLocation relationToChild) {
        this.firstName = firstName;
        this.lastName = lastName;
        this.contactNumber = contactNumber;
        this.relationToChild = relationToChild;
    }

    public String getFirstName() {
        return firstName;
    }

    public String getLastName() {
        return lastName;
    }

    public String getContactNumber() {
        return contactNumber;
    }

    public GeoLocation getRelationToChild() {
        return relationToChild;
    }
}