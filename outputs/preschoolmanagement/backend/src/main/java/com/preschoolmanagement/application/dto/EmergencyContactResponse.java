package com.preschoolmanagement.application.dto;

public class EmergencyContactResponse {

    private final String id;
    private final String name;
    private final String relationship;
    private final String phoneNumber;

    public EmergencyContactResponse(String id, String name, String relationship, String phoneNumber) {
        this.id = id;
        this.name = name;
        this.relationship = relationship;
        this.phoneNumber = phoneNumber;
    }

    public String getId() { return id; }
    public String getName() { return name; }
    public String getRelationship() { return relationship; }
    public String getPhoneNumber() { return phoneNumber; }
}
