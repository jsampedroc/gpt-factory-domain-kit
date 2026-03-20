package com.dentalclinic.dentist.infrastructure.persistence.spring;

import com.dentalclinic.dentist.infrastructure.persistence.entity.DentistJpaEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.JpaSpecificationExecutor;
import java.util.UUID;

public interface SpringDataDentistRepository
        extends JpaRepository<DentistJpaEntity, UUID>,
                JpaSpecificationExecutor<DentistJpaEntity> {
    long countByActiveTrue();
}
