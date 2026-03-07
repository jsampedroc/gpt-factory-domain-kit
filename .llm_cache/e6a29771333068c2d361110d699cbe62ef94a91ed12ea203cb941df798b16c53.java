package com.preschoolmanagement.parent.shared.application.dto;

import java.util.List;
import java.util.UUID;

public class ParentResponse {

    private final UUID id;
    private final String firstName;
    private final String lastName;
    private final String contactNumber;
    private final AddressResponse address;
    private final List<ChildResponse> children;

    public ParentResponse(
            UUID id,
            String firstName,
            String lastName,
            String contactNumber,
            AddressResponse address,
            List<ChildResponse> children
    ) {
        this.id = id;
        this.firstName = firstName;
        this.lastName = lastName;
        this.contactNumber = contactNumber;
        this.address = address;
        this.children = children;
    }

    public UUID id() {
        return id;
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

    public AddressResponse address() {
        return address;
    }

    public List<ChildResponse> children() {
        return children;
    }
}