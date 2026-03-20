package com.dentalclinic.clinical.domain;

import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

public interface EncounterRepository extends JpaRepository<Encounter, UUID> {
    List<Encounter> findByPatientIdAndDeletedFalseOrderByEncounterDateDesc(UUID patientId);
    Optional<Encounter> findByIdAndClinicId(UUID id, UUID clinicId);
    List<Encounter> findByClinicIdAndDeletedFalseOrderByEncounterDateDesc(UUID clinicId);
}
