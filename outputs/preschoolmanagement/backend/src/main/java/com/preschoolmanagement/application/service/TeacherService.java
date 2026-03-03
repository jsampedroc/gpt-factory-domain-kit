package com.preschoolmanagement.application.service;

import com.preschoolmanagement.domain.model.Teacher;
import com.preschoolmanagement.domain.repository.TeacherRepository;
import com.preschoolmanagement.domain.valueobject.TeacherId;

public class TeacherService {

    private final TeacherRepository repository;

    public TeacherService(TeacherRepository repository) {
        this.repository = repository;
    }

    public Teacher findById(TeacherId id) {
        return repository.findById(id)
                .orElseThrow(() -> new IllegalArgumentException("Teacher not found"));
    }

    public void save(Teacher teacher) {
        repository.save(teacher);
    }
}
