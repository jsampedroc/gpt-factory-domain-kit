package com.preschoolmanagement.child.application.dto;

public class AuthorizedPickupResponse {

    private final String firstName;
    private final String lastName;
    private final String relationship;
    private final String contactNumber;

    public AuthorizedPickupResponse(String firstName, String lastName, String relationship, String contactNumber) {
        this.firstName = firstName;
        this.lastName = lastName;
        this.relationship = relationship;
        this.contactNumber = contactNumber;
    }

    public String firstName() { return firstName; }
    public String lastName() { return lastName; }
    public String relationship() { return relationship; }
    public String contactNumber() { return contactNumber; }
}