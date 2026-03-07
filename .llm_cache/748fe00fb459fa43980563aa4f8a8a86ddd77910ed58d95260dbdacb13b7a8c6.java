package com.preschoolmanagement.parent.infrastructure.persistence.adapter;

import com.preschoolmanagement.parent.domain.model.Parent;
import com.preschoolmanagement.parent.domain.repository.ParentRepository;
import com.preschoolmanagement.parent.domain.valueobject.ParentId;
import com.preschoolmanagement.parent.infrastructure.persistence.entity.ParentJpaEntity;
import com.preschoolmanagement.parent.infrastructure.persistence.spring.SpringDataParentRepository;
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
                parent.firstName(),
                parent.lastName(),
                parent.contactNumber(),
                parent.address(),
                parent.children()
        );
        ParentJpaEntity saved = repo.save(entity);
        return new Parent(
                new ParentId(saved.getId()),
                saved.getFirstName(),
                saved.getLastName(),
                saved.getContactNumber(),
                saved.getAddress(),
                saved.getChildren()
        );
    }

    @Override
    public Optional<Parent> findById(ParentId id) {
        return repo.findById(id.value())
                .map(e -> new Parent(
                        new ParentId(e.getId()),
                        e.getFirstName(),
                        e.getLastName(),
                        e.getContactNumber(),
                        e.getAddress(),
                        e.getChildren()
                ));
    }
}