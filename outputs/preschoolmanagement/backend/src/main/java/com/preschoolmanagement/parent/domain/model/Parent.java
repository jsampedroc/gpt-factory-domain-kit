package com.preschoolmanagement.parent.domain.model;

import com.preschoolmanagement.domain.shared.Entity;
import com.preschoolmanagement.parent.domain.valueobject.ParentId;
import java.util.List;

public class Parent extends Entity<ParentId> {

    private final String firstName;
    private final String lastName;
    private final List<Child> children;

    public Parent(ParentId id, String firstName, String lastName, List<Child> children) {
        super(id);
        this.firstName = firstName;
        this.lastName = lastName;
        this.children = children;
    }

    public String getFirstName() { return this.firstName; }

    public String getLastName() { return this.lastName; }

    public List<Child> getChildren() { return this.children; }

}
