package com.dentalclinic.treatment.infrastructure.persistence.spring;

import com.dentalclinic.treatment.infrastructure.persistence.entity.TreatmentJpaEntity;
import java.util.List;
import java.util.UUID;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.JpaSpecificationExecutor;

public interface SpringDataTreatmentRepository
        extends JpaRepository<TreatmentJpaEntity, UUID>,
                JpaSpecificationExecutor<TreatmentJpaEntity> {

    List<TreatmentJpaEntity> findByClinicIdAndDeletedFalse(UUID clinicId);

    long countByDeletedFalse();
}
