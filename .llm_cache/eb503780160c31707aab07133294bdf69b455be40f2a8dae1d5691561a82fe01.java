package com.preschoolmanagement.child.infrastructure.persistence.spring;

import com.preschoolmanagement.child.infrastructure.persistence.entity.AuthorizedPickupJpaEntity;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.UUID;

public interface SpringDataAuthorizedPickupRepository extends JpaRepository<AuthorizedPickupJpaEntity, UUID> {
}