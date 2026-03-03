package com.preschoolmanagement.infrastructure.persistence.spring;

import com.preschoolmanagement.infrastructure.persistence.entity.EmergencyContactJpaEntity;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.UUID;

public interface SpringDataEmergencyContactRepository extends JpaRepository<EmergencyContactJpaEntity, UUID> {
}
