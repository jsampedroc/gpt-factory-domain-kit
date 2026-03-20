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
 * Deactivates a Dentist record
 */
@Service
public class DeactivateDentistUseCase {

    private final DentistRepository repository;

    public DeactivateDentistUseCase(DentistRepository repository) {
        this.repository = repository;
    }

    @Caching(evict = {
        @CacheEvict(value = "entityById", allEntries = true),
        @CacheEvict(value = "dashboard", allEntries = true)
    })
    public void execute(DeactivateDentistCommand command) {
        repository.deactivate(command.dentistId());
    }
}