package com.preschoolmanagement.child.infrastructure.persistence.spring;

import com.preschoolmanagement.child.infrastructure.persistence.entity.AllergyJpaEntity;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.UUID;

public interface SpringDataAllergyRepository extends JpaRepository<AllergyJpaEntity, UUID> {
}