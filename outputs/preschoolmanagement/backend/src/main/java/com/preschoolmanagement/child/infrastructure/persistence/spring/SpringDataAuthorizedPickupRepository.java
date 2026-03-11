package com.preschoolmanagement.child.infrastructure.persistence.spring;

import com.preschoolmanagement.child.domain.repository.JpaRepository;
import com.preschoolmanagement.child.infrastructure.persistence.entity.AuthorizedPickupJpaEntity;




public interface SpringDataAuthorizedPickupRepository extends JpaRepository<AuthorizedPickupJpaEntity, UUID> {
}
