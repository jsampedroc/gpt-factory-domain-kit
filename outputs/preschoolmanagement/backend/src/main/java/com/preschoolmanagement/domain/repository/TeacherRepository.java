package com.preschoolmanagement.domain.repository;

import com.preschoolmanagement.domain.model.Teacher;
import com.preschoolmanagement.domain.valueobject.TeacherId;

import java.util.Optional;

public interface TeacherRepository {

    Optional<Teacher> findById(TeacherId id);

    void save(Teacher entity);
}
