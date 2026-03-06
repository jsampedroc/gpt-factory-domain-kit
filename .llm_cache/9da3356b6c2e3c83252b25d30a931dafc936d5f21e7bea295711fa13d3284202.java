package com.preschoolmanagement.child.application.dto;

import com.preschoolmanagement.domain.valueobject.GeoLocation;

public class AuthorizedPickupResponse {

    private final String firstName;
    private final String lastName;
    private final String contactNumber;
    private final GeoLocation relationToChild;

    public AuthorizedPickupResponse(
            String firstName,
            String lastName,
            String contactNumber,
            GeoLocation relationToChild
    ) {
        this.firstName = firstName;
        this.lastName = lastName;
        this.contactNumber = contactNumber;
        this.relationToChild = relationToChild;
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

    public GeoLocation relationToChild() {
        return relationToChild;
    }
}