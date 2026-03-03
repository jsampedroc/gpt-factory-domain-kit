package com.preschoolmanagement.infrastructure.persistence.spring;

import com.preschoolmanagement.infrastructure.persistence.entity.ActivityLogJpaEntity;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.UUID;

public interface SpringDataActivityLogRepository extends JpaRepository<ActivityLogJpaEntity, UUID> {
}
