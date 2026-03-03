package com.preschoolmanagement.infrastructure.persistence.adapter;

import com.preschoolmanagement.domain.model.Child;
import com.preschoolmanagement.domain.repository.ChildRepository;
import com.preschoolmanagement.domain.valueobject.ChildId;
import com.preschoolmanagement.infrastructure.persistence.entity.ChildJpaEntity;
import com.preschoolmanagement.infrastructure.persistence.spring.SpringDataChildRepository;
import org.springframework.stereotype.Repository;

import java.util.Objects;
import java.util.Optional;

@Repository
public class JpaChildRepositoryAdapter implements ChildRepository {

    private final SpringDataChildRepository repo;

    public JpaChildRepositoryAdapter(SpringDataChildRepository repo) {
        this.repo = Objects.requireNonNull(repo);
    }

    @Override
    public Child save(Child child) {
        ChildJpaEntity entity = new ChildJpaEntity(
                child.id().value(),
                child.name()
        );
        ChildJpaEntity saved = repo.save(entity);
        return new Child(
                new ChildId(saved.getId()),
                saved.getName()
        );
    }

    @Override
    public Optional<Child> findById(ChildId id) {
        return repo.findById(id.value())
                .map(e -> new Child(new ChildId(e.getId()), e.getName()));
    }
}
