package com.preschoolmanagement.domain.repository;

import com.preschoolmanagement.domain.model.TuitionPlan;
import com.preschoolmanagement.domain.valueobject.TuitionPlanId;

import java.util.Optional;

public interface TuitionPlanRepository {

    Optional<TuitionPlan> findById(TuitionPlanId id);

    void save(TuitionPlan entity);
}
