package com.preschoolmanagement.parent.shared.application.dto;

import jakarta.validation.constraints.NotBlank;
import java.util.List;

public class ParentRequest {

    @NotBlank
    private String firstName;

    @NotBlank
    private String lastName;

    @NotBlank
    private String contactNumber;

    private AddressRequest address;

    private List<ChildRequest> children;

    public ParentRequest() {
    }

    public ParentRequest(String firstName, String lastName, String contactNumber, AddressRequest address, List<ChildRequest> children) {
        this.firstName = firstName;
        this.lastName = lastName;
        this.contactNumber = contactNumber;
        this.address = address;
        this.children = children;
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

    public AddressRequest address() {
        return address;
    }

    public List<ChildRequest> children() {
        return children;
    }
}