package com.example.infrastructure.persistence;

import com.example.domain.model.Example;
import com.example.domain.repository.ExampleRepository;
import com.example.domain.valueobject.ExampleId;
import org.springframework.data.jpa.repository.JpaRepository;

public interface JpaExampleRepository
        extends JpaRepository<Example, ExampleId>, ExampleRepository {
}