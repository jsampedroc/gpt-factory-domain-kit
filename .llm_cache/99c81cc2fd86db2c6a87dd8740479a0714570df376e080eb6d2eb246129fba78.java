package com.preschoolmanagement.parent.application.dto;

import com.preschoolmanagement.domain.child.model.Child;
import com.preschoolmanagement.domain.shared.valueobject.Address;

import java.util.List;

public class ParentResponse {

    private final String firstName;
    private final String lastName;
    private final String contactNumber;
    private final Address address;
    private final List<Child> children;

    public ParentResponse(String firstName, String lastName, String contactNumber, Address address, List<Child> children) {
        this.firstName = firstName;
        this.lastName = lastName;
        this.contactNumber = contactNumber;
        this.address = address;
        this.children = children;
    }

    public String firstName() { return firstName; }
    public String lastName() { return lastName; }
    public String contactNumber() { return contactNumber; }
    public Address address() { return address; }
    public List<Child> children() { return children; }
}