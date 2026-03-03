package com.example.application.service;

import com.example.domain.model.Example;
import com.example.domain.repository.ExampleRepository;
import com.example.domain.valueobject.ExampleId;

public class ExampleService {

    private final ExampleRepository repository;

    public ExampleService(ExampleRepository repository) {
        this.repository = repository;
    }

    public Example findById(ExampleId id) {
        return repository.findById(id)
                .orElseThrow(() -> new IllegalArgumentException("Example not found"));
    }

    public void save(Example example) {
        repository.save(example);
    }
}