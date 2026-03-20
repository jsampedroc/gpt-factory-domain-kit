package com.dentalclinic.treatment.domain;

import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

public interface TreatmentPlanRepository extends JpaRepository<TreatmentPlan, UUID> {
    List<TreatmentPlan> findByPatientIdAndDeletedFalse(UUID patientId);
    List<TreatmentPlan> findByClinicIdAndDeletedFalseOrderByCreatedAtDesc(UUID clinicId);
    Optional<TreatmentPlan> findByIdAndClinicId(UUID id, UUID clinicId);
}
