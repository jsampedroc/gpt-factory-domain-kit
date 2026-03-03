package com.example.infrastructure.persistence.spring;

import com.example.infrastructure.persistence.entity.ExampleJpaEntity;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.UUID;

public interface SpringDataExampleRepository extends JpaRepository<ExampleJpaEntity, UUID> {
}