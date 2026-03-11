package com.preschoolmanagement.parent.infrastructure.persistence.spring;

import com.preschoolmanagement.parent.domain.repository.JpaRepository;
import com.preschoolmanagement.parent.infrastructure.persistence.entity.ParentJpaEntity;
import java.util.List;




public interface SpringDataParentRepository extends JpaRepository<ParentJpaEntity, UUID> {
}
