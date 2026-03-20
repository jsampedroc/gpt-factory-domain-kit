package com.dentalclinic.patient.application.usecase;

import com.dentalclinic.patient.domain.model.Patient;
import com.dentalclinic.patient.domain.repository.PatientRepository;
import com.dentalclinic.patient.domain.valueobject.PatientId;
import java.util.UUID;
import java.util.Optional;
import java.util.List;
import org.springframework.cache.annotation.CacheEvict;
import org.springframework.cache.annotation.Caching;
import org.springframework.stereotype.Service;

/**
 * Deactivates a Patient record
 */
@Service
public class DeactivatePatientUseCase {

    private final PatientRepository repository;

    public DeactivatePatientUseCase(PatientRepository repository) {
        this.repository = repository;
    }

    @Caching(evict = {
        @CacheEvict(value = "entityById", allEntries = true),
        @CacheEvict(value = "dashboard", allEntries = true)
    })
    public void execute(DeactivatePatientCommand command) {
        repository.deactivate(command.patientId());
    }
}