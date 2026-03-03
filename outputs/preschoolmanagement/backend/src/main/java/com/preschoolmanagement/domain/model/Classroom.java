package com.preschoolmanagement.domain.model;

import com.preschoolmanagement.domain.shared.Entity;
import com.preschoolmanagement.domain.valueobject.ClassroomId;


public class Classroom extends Entity<ClassroomId> {

    public Classroom(ClassroomId id) {
        super(id);
    }
}
