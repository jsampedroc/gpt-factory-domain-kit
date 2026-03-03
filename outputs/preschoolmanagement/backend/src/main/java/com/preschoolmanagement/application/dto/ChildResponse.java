package com.preschoolmanagement.application.dto;

public class ChildResponse {

    private final String id;
    private final String firstName;
    private final String lastName;
    private final String dateOfBirth;
    private final String parentName;
    private final String parentPhone;
    private final String status;

    public ChildResponse(String id, String firstName, String lastName, String dateOfBirth, String parentName, String parentPhone, String status) {
        this.id = id;
        this.firstName = firstName;
        this.lastName = lastName;
        this.dateOfBirth = dateOfBirth;
        this.parentName = parentName;
        this.parentPhone = parentPhone;
        this.status = status;
    }

    public String getId() { return id; }
    public String getFirstName() { return firstName; }
    public String getLastName() { return lastName; }
    public String getDateOfBirth() { return dateOfBirth; }
    public String getParentName() { return parentName; }
    public String getParentPhone() { return parentPhone; }
    public String getStatus() { return status; }
}
