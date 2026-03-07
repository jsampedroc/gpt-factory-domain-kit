package com.preschoolmanagement.child.infrastructure.persistence.spring;

import com.preschoolmanagement.child.infrastructure.persistence.entity.ImmunizationJpaEntity;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.UUID;

public interface SpringDataImmunizationRepository extends JpaRepository<ImmunizationJpaEntity, UUID> {
}