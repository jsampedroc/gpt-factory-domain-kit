package com.preschoolmanagement.parent.infrastructure.persistence.spring;

import com.preschoolmanagement.parent.infrastructure.persistence.entity.ParentJpaEntity;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.UUID;

public interface SpringDataParentRepository extends JpaRepository<ParentJpaEntity, UUID> {
}