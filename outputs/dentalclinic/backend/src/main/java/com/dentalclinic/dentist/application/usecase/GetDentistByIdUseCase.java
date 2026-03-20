package com.dentalclinic.dentist.application.usecase;

import com.dentalclinic.dentist.domain.model.Dentist;
import com.dentalclinic.dentist.domain.repository.DentistRepository;
import com.dentalclinic.dentist.domain.valueobject.DentistId;
import java.util.UUID;
import java.util.Optional;
import java.util.List;
import org.springframework.cache.annotation.Cacheable;
import org.springframework.stereotype.Service;

/**
 * Retrieves a Dentist by its identifier
 */
@Service
public class GetDentistByIdUseCase {

    private final DentistRepository repository;

    public GetDentistByIdUseCase(DentistRepository repository) {
        this.repository = repository;
    }

    @Cacheable(value = "entityById", key = "#query.dentistId()")
    public Optional<Dentist> execute(GetDentistByIdQuery query) {
        return repository.findById(query.dentistId());
    }
}