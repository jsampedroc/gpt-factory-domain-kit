package com.dentalclinic.patient.application.usecase;

import com.dentalclinic.patient.domain.model.Patient;
import com.dentalclinic.patient.domain.repository.PatientRepository;
import com.dentalclinic.patient.domain.valueobject.PatientId;
import java.util.UUID;
import java.util.Optional;
import java.util.List;
import org.springframework.cache.annotation.Cacheable;
import org.springframework.stereotype.Service;

/**
 * Retrieves a Patient by its identifier
 */
@Service
public class GetPatientByIdUseCase {

    private final PatientRepository repository;

    public GetPatientByIdUseCase(PatientRepository repository) {
        this.repository = repository;
    }

    @Cacheable(value = "entityById", key = "#query.patientId()")
    public Optional<Patient> execute(GetPatientByIdQuery query) {
        return repository.findById(query.patientId());
    }
}