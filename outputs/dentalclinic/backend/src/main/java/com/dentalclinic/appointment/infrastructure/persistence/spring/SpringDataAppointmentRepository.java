package com.dentalclinic.appointment.infrastructure.persistence.spring;

import com.dentalclinic.appointment.infrastructure.persistence.entity.AppointmentJpaEntity;
import java.util.List;
import java.util.UUID;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.JpaSpecificationExecutor;

public interface SpringDataAppointmentRepository
        extends JpaRepository<AppointmentJpaEntity, UUID>,
                JpaSpecificationExecutor<AppointmentJpaEntity> {

    List<AppointmentJpaEntity> findByClinicIdAndDeletedFalse(UUID clinicId);

    long countByDeletedFalse();
}
