package com.preschoolmanagement.child.infrastructure.persistence.spring;

import com.preschoolmanagement.child.domain.repository.JpaRepository;
import com.preschoolmanagement.child.infrastructure.persistence.entity.ChildJpaEntity;
import java.time.LocalDate;
import java.util.List;




public interface SpringDataChildRepository extends JpaRepository<ChildJpaEntity, UUID> {
}
