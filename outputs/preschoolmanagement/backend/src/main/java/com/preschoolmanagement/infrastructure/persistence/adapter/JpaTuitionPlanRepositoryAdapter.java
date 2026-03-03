package com.preschoolmanagement.infrastructure.persistence.adapter;

import com.preschoolmanagement.domain.model.TuitionPlan;
import com.preschoolmanagement.domain.repository.TuitionPlanRepository;
import com.preschoolmanagement.domain.valueobject.TuitionPlanId;
import com.preschoolmanagement.infrastructure.persistence.entity.TuitionPlanJpaEntity;
import com.preschoolmanagement.infrastructure.persistence.spring.SpringDataTuitionPlanRepository;
import org.springframework.stereotype.Repository;

import java.util.Objects;
import java.util.Optional;

@Repository
public class JpaTuitionPlanRepositoryAdapter implements TuitionPlanRepository {

    private final SpringDataTuitionPlanRepository repo;

    public JpaTuitionPlanRepositoryAdapter(SpringDataTuitionPlanRepository repo) {
        this.repo = Objects.requireNonNull(repo);
    }

    @Override
    public TuitionPlan save(TuitionPlan tuitionPlan) {
        TuitionPlanJpaEntity entity = new TuitionPlanJpaEntity(
                tuitionPlan.id().value(),
                tuitionPlan.name()
        );
        TuitionPlanJpaEntity saved = repo.save(entity);
        return new TuitionPlan(
                new TuitionPlanId(saved.getId()),
                saved.getName()
        );
    }

    @Override
    public Optional<TuitionPlan> findById(TuitionPlanId id) {
        return repo.findById(id.value())
                .map(e -> new TuitionPlan(new TuitionPlanId(e.getId()), e.getName()));
    }
}
