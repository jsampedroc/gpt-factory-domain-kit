package com.dentalclinic.patient.infrastructure.persistence.spring;

import com.dentalclinic.patient.infrastructure.persistence.entity.PatientJpaEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.JpaSpecificationExecutor;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

public interface SpringDataPatientRepository
        extends JpaRepository<PatientJpaEntity, UUID>,
                JpaSpecificationExecutor<PatientJpaEntity> {

    List<PatientJpaEntity> findByClinicIdAndDeletedFalse(UUID clinicId);

    Optional<PatientJpaEntity> findByIdAndClinicId(UUID id, UUID clinicId);

    long countByActiveTrue();
}
