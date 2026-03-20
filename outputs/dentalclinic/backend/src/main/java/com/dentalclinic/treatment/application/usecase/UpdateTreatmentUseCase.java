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
 * Updates an existing Treatment
 */
@Service
public class UpdateTreatmentUseCase {

    private final TreatmentRepository repository;

    public UpdateTreatmentUseCase(TreatmentRepository repository) {
        this.repository = repository;
    }

    @Caching(evict = {
        @CacheEvict(value = "entityById", key = "#command.treatmentId()"),
        @CacheEvict(value = "dashboard", allEntries = true)
    })
    public Treatment execute(UpdateTreatmentCommand command) {
        return repository.findById(command.treatmentId())
            .orElseThrow(() -> new IllegalArgumentException("Not found"));
    }
}