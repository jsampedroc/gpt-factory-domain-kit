package com.preschoolmanagement.parent.infrastructure.persistence.adapter;

import com.preschoolmanagement.parent.domain.repository.ParentRepository;
import com.preschoolmanagement.parent.domain.repository.SpringDataParentRepository;
import com.preschoolmanagement.parent.domain.valueobject.ParentId;
import com.preschoolmanagement.parent.infrastructure.persistence.entity.ParentJpaEntity;
import java.util.List;
import java.util.Objects;
import java.util.Optional;
import org.springframework.stereotype.Repository;




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
                parent.lastName()
        );
        ParentJpaEntity saved = repo.save(entity);
        return new Parent(
                new ParentId(saved.getId()),
                saved.getFirstName(),
                saved.getLastName(),
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
                        e.getChildren()
                ));
    }
}
