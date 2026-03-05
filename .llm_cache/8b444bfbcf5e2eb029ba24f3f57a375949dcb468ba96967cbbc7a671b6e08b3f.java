package com.preschoolmanagement.infrastructure.persistence.adapter;

import com.preschoolmanagement.domain.model.Allergy;
import com.preschoolmanagement.domain.repository.AllergyRepository;
import com.preschoolmanagement.domain.valueobject.AllergyId;
import com.preschoolmanagement.infrastructure.persistence.entity.AllergyJpaEntity;
import com.preschoolmanagement.infrastructure.persistence.spring.SpringDataAllergyRepository;
import org.springframework.stereotype.Repository;

import java.util.Objects;
import java.util.Optional;

@Repository
public class JpaAllergyRepositoryAdapter implements AllergyRepository {

    private final SpringDataAllergyRepository repo;

    public JpaAllergyRepositoryAdapter(SpringDataAllergyRepository repo) {
        this.repo = Objects.requireNonNull(repo);
    }

    @Override
    public Allergy save(Allergy allergy) {
        AllergyJpaEntity entity = new AllergyJpaEntity(
                allergy.id().value(),
                allergy.name(),
                allergy.severity()
        );
        AllergyJpaEntity saved = repo.save(entity);
        return new Allergy(
                new AllergyId(saved.getId()),
                saved.getName(),
                saved.getSeverity()
        );
    }

    @Override
    public Optional<Allergy> findById(AllergyId id) {
        return repo.findById(id.value())
                .map(e -> new Allergy(new AllergyId(e.getId()), e.getName(), e.getSeverity()));
    }
}