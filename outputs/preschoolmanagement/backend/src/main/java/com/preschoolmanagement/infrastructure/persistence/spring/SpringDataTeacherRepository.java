package com.preschoolmanagement.infrastructure.persistence.spring;

import com.preschoolmanagement.infrastructure.persistence.entity.TeacherJpaEntity;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.UUID;

public interface SpringDataTeacherRepository extends JpaRepository<TeacherJpaEntity, UUID> {
}
