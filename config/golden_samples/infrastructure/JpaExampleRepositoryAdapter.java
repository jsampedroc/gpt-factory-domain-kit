package com.example.infrastructure.persistence.adapter;

import com.example.domain.model.Example;
import com.example.domain.repository.ExampleRepository;
import com.example.domain.valueobject.ExampleId;
import com.example.infrastructure.persistence.entity.ExampleJpaEntity;
import com.example.infrastructure.persistence.spring.SpringDataExampleRepository;
import org.springframework.stereotype.Repository;

import java.util.Objects;
import java.util.Optional;

@Repository
public class JpaExampleRepositoryAdapter implements ExampleRepository {

    private final SpringDataExampleRepository repo;

    public JpaExampleRepositoryAdapter(SpringDataExampleRepository repo) {
        this.repo = Objects.requireNonNull(repo);
    }

    @Override
    public Example save(Example example) {
        ExampleJpaEntity entity = new ExampleJpaEntity(
                example.id().value(),
                example.name()
        );
        ExampleJpaEntity saved = repo.save(entity);
        return new Example(
                new ExampleId(saved.getId()),
                saved.getName()
        );
    }

    @Override
    public Optional<Example> findById(ExampleId id) {
        return repo.findById(id.value())
                .map(e -> new Example(new ExampleId(e.getId()), e.getName()));
    }
}