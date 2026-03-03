package com.preschoolmanagement.application.service;

import com.preschoolmanagement.domain.model.Parent;
import com.preschoolmanagement.domain.repository.ParentRepository;
import com.preschoolmanagement.domain.valueobject.ParentId;

public class ParentService {

    private final ParentRepository repository;

    public ParentService(ParentRepository repository) {
        this.repository = repository;
    }

    public Parent findById(ParentId id) {
        return repository.findById(id)
                .orElseThrow(() -> new IllegalArgumentException("Parent not found"));
    }

    public void save(Parent parent) {
        repository.save(parent);
    }
}
