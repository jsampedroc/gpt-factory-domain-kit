package com.preschoolmanagement.infrastructure.persistence.spring;

import com.preschoolmanagement.infrastructure.persistence.entity.ClassroomJpaEntity;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.UUID;

public interface SpringDataClassroomRepository extends JpaRepository<ClassroomJpaEntity, UUID> {
}
