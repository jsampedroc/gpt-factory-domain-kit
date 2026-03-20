package com.dentalclinic.patient.api;

import java.util.List;
import java.util.Optional;
import java.util.UUID;

public interface PatientService {
    PatientDto create(CreatePatientRequest request, UUID clinicId);
    Optional<PatientDto> findById(UUID id, UUID clinicId);
    List<PatientDto> findAll(UUID clinicId);
    List<PatientDto> search(UUID clinicId, String query);
    PatientDto update(UUID id, UpdatePatientRequest request, UUID clinicId);
    void delete(UUID id, UUID clinicId);
    long count(UUID clinicId);
}
