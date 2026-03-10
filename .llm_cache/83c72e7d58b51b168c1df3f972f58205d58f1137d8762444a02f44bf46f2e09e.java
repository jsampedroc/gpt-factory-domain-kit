package com.preschoolmanagement.child.infrastructure.persistence.adapter;

import com.preschoolmanagement.child.domain.model.AuthorizedPickup;
import com.preschoolmanagement.child.domain.repository.AuthorizedPickupRepository;
import com.preschoolmanagement.child.domain.valueobject.AuthorizedPickupId;
import com.preschoolmanagement.child.infrastructure.persistence.entity.AuthorizedPickupJpaEntity;
import com.preschoolmanagement.child.infrastructure.persistence.spring.SpringDataAuthorizedPickupRepository;
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
                authorizedPickup.relationship(),
                authorizedPickup.contactNumber()
        );
        AuthorizedPickupJpaEntity saved = repo.save(entity);
        return new AuthorizedPickup(
                new AuthorizedPickupId(saved.getId()),
                saved.getFirstName(),
                saved.getLastName(),
                saved.getRelationship(),
                saved.getContactNumber()
        );
    }

    @Override
    public Optional<AuthorizedPickup> findById(AuthorizedPickupId id) {
        return repo.findById(id.value())
                .map(e -> new AuthorizedPickup(
                        new AuthorizedPickupId(e.getId()),
                        e.getFirstName(),
                        e.getLastName(),
                        e.getRelationship(),
                        e.getContactNumber()
                ));
    }
}