package com.preschoolmanagement.parent.domain.model;

import com.preschoolmanagement.domain.shared.Entity;
import com.preschoolmanagement.parent.domain.valueobject.Address;
import com.preschoolmanagement.parent.domain.valueobject.ParentId;
import java.util.List;

public class Parent extends Entity<ParentId> {

    private final String firstName;
    private final String lastName;
    private final String contactNumber;
    private final Address address;
    private final List<Child> children;

    public Parent(ParentId id, String firstName, String lastName, String contactNumber, Address address, List<Child> children) {
        super(id);
        this.firstName = firstName;
        this.lastName = lastName;
        this.contactNumber = contactNumber;
        this.address = address;
        this.children = children;
    }

    public String getFirstName() { return this.firstName; }

    public String getLastName() { return this.lastName; }

    public String getContactNumber() { return this.contactNumber; }

    public Address getAddress() { return this.address; }

    public List<Child> getChildren() { return this.children; }

}
