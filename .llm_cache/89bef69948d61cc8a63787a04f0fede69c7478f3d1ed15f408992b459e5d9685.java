package com.preschoolmanagement.child.infrastructure.persistence.adapter;

import com.preschoolmanagement.child.domain.model.Immunization;
import com.preschoolmanagement.child.domain.repository.ImmunizationRepository;
import com.preschoolmanagement.child.domain.valueobject.ImmunizationId;
import com.preschoolmanagement.child.infrastructure.persistence.entity.ImmunizationJpaEntity;
import com.preschoolmanagement.child.infrastructure.persistence.spring.SpringDataImmunizationRepository;
import org.springframework.stereotype.Repository;

import java.util.Objects;
import java.util.Optional;

@Repository
public class JpaImmunizationRepositoryAdapter implements ImmunizationRepository {

    private final SpringDataImmunizationRepository repo;

    public JpaImmunizationRepositoryAdapter(SpringDataImmunizationRepository repo) {
        this.repo = Objects.requireNonNull(repo);
    }

    @Override
    public Immunization save(Immunization immunization) {
        ImmunizationJpaEntity entity = new ImmunizationJpaEntity(
                immunization.id().value(),
                immunization.vaccineName(),
                immunization.dateAdministered()
        );
        ImmunizationJpaEntity saved = repo.save(entity);
        return new Immunization(
                new ImmunizationId(saved.getId()),
                saved.getVaccineName(),
                saved.getDateAdministered()
        );
    }

    @Override
    public Optional<Immunization> findById(ImmunizationId id) {
        return repo.findById(id.value())
                .map(e -> new Immunization(
                        new ImmunizationId(e.getId()),
                        e.getVaccineName(),
                        e.getDateAdministered()
                ));
    }
}