package com.dentalclinic.dentist.application.usecase;

import com.dentalclinic.dentist.domain.model.Dentist;
import com.dentalclinic.dentist.domain.repository.DentistRepository;
import com.dentalclinic.dentist.domain.valueobject.DentistId;
import java.util.UUID;
import java.util.Optional;
import java.util.List;
import org.springframework.cache.annotation.CacheEvict;
import org.springframework.cache.annotation.Caching;
import org.springframework.stereotype.Service;

/**
 * Updates an existing Dentist
 */
@Service
public class UpdateDentistUseCase {

    private final DentistRepository repository;

    public UpdateDentistUseCase(DentistRepository repository) {
        this.repository = repository;
    }

    @Caching(evict = {
        @CacheEvict(value = "entityById", key = "#command.dentistId()"),
        @CacheEvict(value = "dashboard", allEntries = true)
    })
    public Dentist execute(UpdateDentistCommand command) {
        return repository.findById(command.dentistId())
            .orElseThrow(() -> new IllegalArgumentException("Not found"));
    }
}