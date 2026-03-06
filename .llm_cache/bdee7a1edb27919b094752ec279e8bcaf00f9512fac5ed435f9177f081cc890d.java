package com.preschoolmanagement.parent.application.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import com.preschoolmanagement.domain.valueobject.Address;
import com.preschoolmanagement.child.domain.model.Child;
import java.util.List;

public class ParentRequest {

    @NotBlank
    private final String firstName;

    @NotBlank
    private final String lastName;

    @NotBlank
    private final String contactNumber;

    @NotNull
    private final Address address;

    @NotNull
    private final List<Child> children;

    public ParentRequest(
            String firstName,
            String lastName,
            String contactNumber,
            Address address,
            List<Child> children) {
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

    public Address address() {
        return address;
    }

    public List<Child> children() {
        return children;
    }
}