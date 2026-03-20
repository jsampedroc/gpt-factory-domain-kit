package com.dentalclinic.dentist.application.usecase;

import com.dentalclinic.dentist.domain.model.Dentist;
import com.dentalclinic.dentist.domain.repository.DentistRepository;
import com.dentalclinic.dentist.domain.valueobject.DentistId;
import java.util.UUID;
import java.util.Optional;
import java.util.List;
import com.dentalclinic.dentist.domain.event.DentistRegisteredEvent;
import org.springframework.context.ApplicationEventPublisher;
import org.springframework.cache.annotation.CacheEvict;
import org.springframework.stereotype.Service;

/**
 * Registers a new Dentist in the system
 */
@Service
public class RegisterDentistUseCase {

    private final DentistRepository repository;
    private final ApplicationEventPublisher publisher;

    public RegisterDentistUseCase(DentistRepository repository, ApplicationEventPublisher publisher) {
        this.repository = repository;
        this.publisher = publisher;
    }

    @CacheEvict(value = "dashboard", allEntries = true)
    public Dentist execute(RegisterDentistCommand command) {
        Dentist dentist = new Dentist(
            new DentistId(UUID.randomUUID()),
            command.firstName(),
            command.lastName(),
            command.licenseNumber(),
            UUID.randomUUID()
        );
        publisher.publishEvent(DentistRegisteredEvent.of(dentist.getId().value(), dentist.getFirstName(), dentist.getLastName(), dentist.getLicenseNumber()));
        return repository.save(dentist);
    }
}