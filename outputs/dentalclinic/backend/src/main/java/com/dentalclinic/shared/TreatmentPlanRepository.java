package com.dentalclinic.shared;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import java.util.List;
import java.util.UUID;

@Repository
public interface TreatmentPlanRepository extends JpaRepository<TreatmentPlan, UUID> {
    List<TreatmentPlan> findByPatientIdOrderByCreatedAtDesc(UUID patientId);
    List<TreatmentPlan> findByStatus(String status);
}
