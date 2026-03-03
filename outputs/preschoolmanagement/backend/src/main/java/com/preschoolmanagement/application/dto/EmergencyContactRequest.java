package com.preschoolmanagement.application.dto;

public class EmergencyContactRequest {

    private final String name;
    private final String relationship;
    private final String phoneNumber;
    private final String email;

    public EmergencyContactRequest(String name, String relationship, String phoneNumber, String email) {
        this.name = name;
        this.relationship = relationship;
        this.phoneNumber = phoneNumber;
        this.email = email;
    }

    public String getName() {
        return name;
    }

    public String getRelationship() {
        return relationship;
    }

    public String getPhoneNumber() {
        return phoneNumber;
    }

    public String getEmail() {
        return email;
    }
}
