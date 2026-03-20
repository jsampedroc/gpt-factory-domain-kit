package com.dentalclinic.patient.application.usecase;

import com.dentalclinic.patient.domain.model.Patient;
import com.dentalclinic.patient.domain.repository.PatientRepository;
import com.dentalclinic.patient.domain.valueobject.PatientId;
import com.dentalclinic.shared.kernel.ClinicContext;
import java.util.UUID;
import java.util.ArrayList;
import com.dentalclinic.patient.domain.event.PatientRegisteredEvent;
import org.springframework.context.ApplicationEventPublisher;
import org.springframework.cache.annotation.CacheEvict;
import org.springframework.stereotype.Service;

/**
 * Registers a new Patient in the system
 */
@Service
public class RegisterPatientUseCase {

    private final PatientRepository repository;
    private final ApplicationEventPublisher publisher;
    private final ClinicContext clinicContext;

    public RegisterPatientUseCase(PatientRepository repository,
                                   ApplicationEventPublisher publisher,
                                   ClinicContext clinicContext) {
        this.repository = repository;
        this.publisher = publisher;
        this.clinicContext = clinicContext;
    }

    @CacheEvict(value = "dashboard", allEntries = true)
    public Patient execute(RegisterPatientCommand command) {
        String fullName = command.fullName() != null ? command.fullName()
                : ((command.firstName() != null ? command.firstName() : "") + " "
                   + (command.lastName() != null ? command.lastName() : "")).trim();

        Patient patient = new Patient(
            new PatientId(UUID.randomUUID()),
            fullName,
            command.firstName(),
            command.lastName(),
            command.birthDate(),
            command.dniNie(),
            command.email(),
            command.phone(),
            command.gender(),
            null,
            command.address(),
            command.city(),
            command.postalCode(),
            null,
            true,
            new ArrayList<>(),
            clinicContext.current(),
            null
        );
        publisher.publishEvent(PatientRegisteredEvent.of(patient.getId().value(), patient.getFirstName(), patient.getLastName()));
        return repository.save(patient);
    }
}
