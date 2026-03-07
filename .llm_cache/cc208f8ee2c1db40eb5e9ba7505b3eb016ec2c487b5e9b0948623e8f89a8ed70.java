package com.preschoolmanagement.child.infrastructure.persistence.spring;

import com.preschoolmanagement.child.infrastructure.persistence.entity.ChildJpaEntity;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.UUID;

public interface SpringDataChildRepository extends JpaRepository<ChildJpaEntity, UUID> {
}