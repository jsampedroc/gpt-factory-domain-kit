package com.preschoolmanagement.domain.model;

import com.preschoolmanagement.domain.shared.Entity;
import com.preschoolmanagement.domain.valueobject.ChildId;


public class Child extends Entity<ChildId> {

    public Child(ChildId id) {
        super(id);
    }
}
