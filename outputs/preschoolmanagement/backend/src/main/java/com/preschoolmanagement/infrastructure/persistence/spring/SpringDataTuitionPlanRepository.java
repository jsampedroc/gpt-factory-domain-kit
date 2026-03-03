package com.preschoolmanagement.infrastructure.persistence.spring;

import com.preschoolmanagement.infrastructure.persistence.entity.TuitionPlanJpaEntity;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.UUID;

public interface SpringDataTuitionPlanRepository extends JpaRepository<TuitionPlanJpaEntity, UUID> {
}
