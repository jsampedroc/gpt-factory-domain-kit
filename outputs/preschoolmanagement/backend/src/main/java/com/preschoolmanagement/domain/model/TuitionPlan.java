package com.preschoolmanagement.domain.model;

import com.preschoolmanagement.domain.shared.Entity;
import com.preschoolmanagement.domain.valueobject.TuitionPlanId;

import java.util.Objects;

public class TuitionPlan extends Entity<TuitionPlanId> {

    private final String name;

    public TuitionPlan(TuitionPlanId id, String name) {
        super(id);
        this.name = Objects.requireNonNull(name);
    }

    public String name() {
        return name;
    }
}
