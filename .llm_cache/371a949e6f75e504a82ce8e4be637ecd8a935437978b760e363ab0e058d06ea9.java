package com.preschoolmanagement.infrastructure.persistence.adapter;

import com.preschoolmanagement.domain.model.AuthorizedPickup;
import com.preschoolmanagement.domain.repository.AuthorizedPickupRepository;
import com.preschoolmanagement.domain.valueobject.AuthorizedPickupId;
import com.preschoolmanagement.infrastructure.persistence.entity.AuthorizedPickupJpaEntity;
import com.preschoolmanagement.infrastructure.persistence.spring.SpringDataAuthorizedPickupRepository;
import org.springframework.stereotype.Repository;

import java.util.Objects;
import java.util.Optional;

@Repository
public class JpaAuthorizedPickupRepositoryAdapter implements AuthorizedPickupRepository {

    private final SpringDataAuthorizedPickupRepository repo;

    public JpaAuthorizedPickupRepositoryAdapter(SpringDataAuthorizedPickupRepository repo) {
        this.repo = Objects.requireNonNull(repo);
    }

    @Override
    public AuthorizedPickup save(AuthorizedPickup authorizedPickup) {
        AuthorizedPickupJpaEntity entity = new AuthorizedPickupJpaEntity(
                authorizedPickup.id().value(),
                authorizedPickup.firstName(),
                authorizedPickup.lastName(),
                authorizedPickup.relationship()
        );
        AuthorizedPickupJpaEntity saved = repo.save(entity);
        return new AuthorizedPickup(
                new AuthorizedPickupId(saved.getId()),
                saved.getFirstName(),
                saved.getLastName(),
                saved.getRelationship()
        );
    }

    @Override
    public Optional<AuthorizedPickup> findById(AuthorizedPickupId id) {
        return repo.findById(id.value())
                .map(e -> new AuthorizedPickup(
                        new AuthorizedPickupId(e.getId()),
                        e.getFirstName(),
                        e.getLastName(),
                        e.getRelationship()
                ));
    }
}