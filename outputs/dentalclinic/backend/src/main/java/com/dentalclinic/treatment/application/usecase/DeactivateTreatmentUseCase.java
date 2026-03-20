package com.dentalclinic.treatment.application.usecase;

import com.dentalclinic.treatment.domain.model.Treatment;
import com.dentalclinic.treatment.domain.repository.TreatmentRepository;
import com.dentalclinic.treatment.domain.valueobject.TreatmentId;
import java.util.UUID;
import java.util.Optional;
import java.util.List;
import org.springframework.cache.annotation.CacheEvict;
import org.springframework.cache.annotation.Caching;
import org.springframework.stereotype.Service;

/**
 * Deactivates a Treatment record
 */
@Service
public class DeactivateTreatmentUseCase {

    private final TreatmentRepository repository;

    public DeactivateTreatmentUseCase(TreatmentRepository repository) {
        this.repository = repository;
    }

    @Caching(evict = {
        @CacheEvict(value = "entityById", allEntries = true),
        @CacheEvict(value = "dashboard", allEntries = true)
    })
    public void execute(DeactivateTreatmentCommand command) {
        repository.deactivate(command.treatmentId());
    }
}