package com.preschoolmanagement.application.service;

import com.preschoolmanagement.domain.model.Child;
import com.preschoolmanagement.domain.repository.ChildRepository;
import com.preschoolmanagement.domain.valueobject.ChildId;

public class ChildService {

    private final ChildRepository repository;

    public ChildService(ChildRepository repository) {
        this.repository = repository;
    }

    public Child findById(ChildId id) {
        return repository.findById(id)
                .orElseThrow(() -> new IllegalArgumentException("Child not found"));
    }

    public void save(Child child) {
        repository.save(child);
    }
}
