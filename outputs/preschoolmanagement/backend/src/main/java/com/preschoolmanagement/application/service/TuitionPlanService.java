package com.preschoolmanagement.application.service;

import com.preschoolmanagement.domain.model.TuitionPlan;
import com.preschoolmanagement.domain.repository.TuitionPlanRepository;
import com.preschoolmanagement.domain.valueobject.TuitionPlanId;

public class TuitionPlanService {

    private final TuitionPlanRepository repository;

    public TuitionPlanService(TuitionPlanRepository repository) {
        this.repository = repository;
    }

    public TuitionPlan findById(TuitionPlanId id) {
        return repository.findById(id)
                .orElseThrow(() -> new IllegalArgumentException("TuitionPlan not found"));
    }

    public void save(TuitionPlan tuitionPlan) {
        repository.save(tuitionPlan);
    }
}
