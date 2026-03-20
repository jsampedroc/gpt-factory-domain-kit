package com.dentalclinic.patient.domain.repository;

import com.dentalclinic.patient.domain.model.Patient;
import com.dentalclinic.shared.PageResult;
import java.util.Optional;
import java.util.UUID;

public interface PatientRepository {

    Patient save(Patient entity);

    Optional<Patient> findById(UUID id);

    PageResult<Patient> findAll(int page, int size, String search);

    void deactivate(UUID id);

}
