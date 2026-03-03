package com.preschoolmanagement.application.service;

import com.preschoolmanagement.domain.model.Classroom;
import com.preschoolmanagement.domain.repository.ClassroomRepository;
import com.preschoolmanagement.domain.valueobject.ClassroomId;

public class ClassroomService {

    private final ClassroomRepository repository;

    public ClassroomService(ClassroomRepository repository) {
        this.repository = repository;
    }

    public Classroom findById(ClassroomId id) {
        return repository.findById(id)
                .orElseThrow(() -> new IllegalArgumentException("Classroom not found"));
    }

    public void save(Classroom classroom) {
        repository.save(classroom);
    }
}
