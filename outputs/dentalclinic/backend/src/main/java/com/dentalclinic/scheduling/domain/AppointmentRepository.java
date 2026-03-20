package com.dentalclinic.scheduling.domain;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

public interface AppointmentRepository extends JpaRepository<Appointment, UUID> {
    List<Appointment> findByClinicIdAndDeletedFalseOrderByStartTimeAsc(UUID clinicId);
    List<Appointment> findByPatientIdAndDeletedFalse(UUID patientId);
    Optional<Appointment> findByIdAndClinicId(UUID id, UUID clinicId);
    @Query("SELECT a FROM Appointment a WHERE a.clinicId = :clinicId AND a.deleted = false " +
           "AND a.startTime >= :from AND a.startTime < :to ORDER BY a.startTime ASC")
    List<Appointment> findByDateRange(UUID clinicId, LocalDateTime from, LocalDateTime to);
    long countByClinicIdAndStatusAndDeletedFalse(UUID clinicId, AppointmentStatus status);
}
