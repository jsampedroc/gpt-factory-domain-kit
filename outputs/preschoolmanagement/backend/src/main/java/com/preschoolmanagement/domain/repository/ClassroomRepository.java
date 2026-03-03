package com.preschoolmanagement.domain.repository;

import com.preschoolmanagement.domain.model.Classroom;
import com.preschoolmanagement.domain.valueobject.ClassroomId;

import java.util.Optional;

public interface ClassroomRepository {

    Optional<Classroom> findById(ClassroomId id);

    void save(Classroom entity);
}
