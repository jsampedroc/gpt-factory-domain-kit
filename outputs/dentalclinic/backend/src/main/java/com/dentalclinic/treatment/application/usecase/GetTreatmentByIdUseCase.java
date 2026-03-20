package com.dentalclinic.treatment.application.usecase;

import com.dentalclinic.treatment.domain.model.Treatment;
import com.dentalclinic.treatment.domain.repository.TreatmentRepository;
import com.dentalclinic.treatment.domain.valueobject.TreatmentId;
import java.util.UUID;
import java.util.Optional;
import java.util.List;
import org.springframework.cache.annotation.Cacheable;
import org.springframework.stereotype.Service;

/**
 * Retrieves a Treatment by its identifier
 */
@Service
public class GetTreatmentByIdUseCase {

    private final TreatmentRepository repository;

    public GetTreatmentByIdUseCase(TreatmentRepository repository) {
        this.repository = repository;
    }

    @Cacheable(value = "entityById", key = "#query.treatmentId()")
    public Optional<Treatment> execute(GetTreatmentByIdQuery query) {
        return repository.findById(query.treatmentId());
    }
}