package com.preschoolmanagement.domain.model;

import com.preschoolmanagement.domain.shared.Entity;
import com.preschoolmanagement.domain.valueobject.TeacherId;


public class Teacher extends Entity<TeacherId> {

    public Teacher(TeacherId id) {
        super(id);
    }
}
