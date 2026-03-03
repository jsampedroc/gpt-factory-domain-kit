package com.example.domain.repository;

import com.example.domain.model.Example;
import com.example.domain.valueobject.ExampleId;

import java.util.Optional;

public interface ExampleRepository {

    Optional<Example> findById(ExampleId id);

    void save(Example entity);
}