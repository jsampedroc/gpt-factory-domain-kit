package com.dentalclinic.patient.domain;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

public interface PatientRepository extends JpaRepository<Patient, UUID> {
    List<Patient> findByClinicIdAndDeletedFalse(UUID clinicId);
    Optional<Patient> findByIdAndClinicId(UUID id, UUID clinicId);
    @Query("SELECT p FROM Patient p WHERE p.clinicId = :clinicId AND p.deleted = false AND " +
           "(LOWER(p.fullName) LIKE LOWER(CONCAT('%', :q, '%')) OR LOWER(p.email) LIKE LOWER(CONCAT('%', :q, '%')) OR p.phone LIKE CONCAT('%', :q, '%'))")
    List<Patient> search(UUID clinicId, String q);
    long countByClinicIdAndDeletedFalse(UUID clinicId);
}
