package com.preschoolmanagement.infrastructure.persistence.adapter;

import com.preschoolmanagement.domain.model.Parent;
import com.preschoolmanagement.domain.repository.ParentRepository;
import com.preschoolmanagement.domain.valueobject.ParentId;
import com.preschoolmanagement.infrastructure.persistence.entity.ParentJpaEntity;
import com.preschoolmanagement.infrastructure.persistence.spring.SpringDataParentRepository;
import org.springframework.stereotype.Repository;

import java.util.Objects;
import java.util.Optional;

@Repository
public class JpaParentRepositoryAdapter implements ParentRepository {

    private final SpringDataParentRepository repo;

    public JpaParentRepositoryAdapter(SpringDataParentRepository repo) {
        this.repo = Objects.requireNonNull(repo);
    }

    @Override
    public Parent save(Parent parent) {
        ParentJpaEntity entity = new ParentJpaEntity(
                parent.id().value(),
                parent.name()
        );
        ParentJpaEntity saved = repo.save(entity);
        return new Parent(
                new ParentId(saved.getId()),
                saved.getName()
        );
    }

    @Override
    public Optional<Parent> findById(ParentId id) {
        return repo.findById(id.value())
                .map(e -> new Parent(new ParentId(e.getId()), e.getName()));
    }
}
