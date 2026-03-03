package com.preschoolmanagement.domain.model;

import com.preschoolmanagement.domain.shared.Entity;
import com.preschoolmanagement.domain.valueobject.ParentId;


public class Parent extends Entity<ParentId> {

    public Parent(ParentId id) {
        super(id);
    }
}
