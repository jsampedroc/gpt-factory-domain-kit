package com.preschoolmanagement.child.infrastructure.persistence.adapter;

import com.preschoolmanagement.child.domain.repository.AuthorizedPickupRepository;
import com.preschoolmanagement.child.domain.repository.SpringDataAuthorizedPickupRepository;
import com.preschoolmanagement.child.domain.valueobject.AuthorizedPickupId;
import com.preschoolmanagement.child.infrastructure.persistence.entity.AuthorizedPickupJpaEntity;
import java.util.Objects;
import java.util.Optional;
import org.springframework.stereotype.Repository;




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
                authorizedPickup.relationshipToChild()
        );
        AuthorizedPickupJpaEntity saved = repo.save(entity);
        return new AuthorizedPickup(
                new AuthorizedPickupId(saved.getId()),
                saved.getFirstName(),
                saved.getLastName(),
                saved.getRelationshipToChild()
        );
    }

    @Override
    public Optional<AuthorizedPickup> findById(AuthorizedPickupId id) {
        return repo.findById(id.value())
                .map(e -> new AuthorizedPickup(
                        new AuthorizedPickupId(e.getId()),
                        e.getFirstName(),
                        e.getLastName(),
                        e.getRelationshipToChild()
                ));
    }
}
