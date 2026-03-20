package com.dentalclinic.shared;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import java.util.List;
import java.util.UUID;

@Repository
public interface TreatmentPlanItemRepository extends JpaRepository<TreatmentPlanItem, UUID> {
    List<TreatmentPlanItem> findByPlanIdOrderByToothNumber(UUID planId);
    void deleteByPlanId(UUID planId);
}
