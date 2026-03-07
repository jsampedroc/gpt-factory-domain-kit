package com.preschoolmanagement.child.infrastructure.persistence.adapter;

import com.preschoolmanagement.child.domain.model.Child;
import com.preschoolmanagement.child.domain.repository.ChildRepository;
import com.preschoolmanagement.child.domain.valueobject.ChildId;
import com.preschoolmanagement.child.infrastructure.persistence.entity.ChildJpaEntity;
import com.preschoolmanagement.child.infrastructure.persistence.spring.SpringDataChildRepository;
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
                child.firstName(),
                child.lastName(),
                child.birthDate(),
                child.allergies(),
                child.immunizations(),
                child.authorizedPickups()
        );
        ChildJpaEntity saved = repo.save(entity);
        return new Child(
                new ChildId(saved.getId()),
                saved.getFirstName(),
                saved.getLastName(),
                saved.getBirthDate(),
                saved.getAllergies(),
                saved.getImmunizations(),
                saved.getAuthorizedPickups()
        );
    }

    @Override
    public Optional<Child> findById(ChildId id) {
        return repo.findById(id.value())
                .map(e -> new Child(
                        new ChildId(e.getId()),
                        e.getFirstName(),
                        e.getLastName(),
                        e.getBirthDate(),
                        e.getAllergies(),
                        e.getImmunizations(),
                        e.getAuthorizedPickups()
                ));
    }
}