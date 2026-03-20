package com.dentalclinic.patient.application.usecase;

import com.dentalclinic.patient.domain.model.Patient;
import com.dentalclinic.patient.domain.repository.PatientRepository;
import com.dentalclinic.patient.domain.valueobject.PatientId;
import java.util.UUID;
import org.springframework.cache.annotation.CacheEvict;
import org.springframework.cache.annotation.Caching;
import org.springframework.stereotype.Service;

/**
 * Updates an existing Patient
 */
@Service
public class UpdatePatientUseCase {

    private final PatientRepository repository;

    public UpdatePatientUseCase(PatientRepository repository) {
        this.repository = repository;
    }

    @Caching(evict = {
        @CacheEvict(value = "entityById", key = "#command.patientId()"),
        @CacheEvict(value = "dashboard", allEntries = true)
    })
    public Patient execute(UpdatePatientCommand command) {
        Patient existing = repository.findById(command.patientId())
            .orElseThrow(() -> new IllegalArgumentException("Not found"));

        String fullName = command.fullName() != null ? command.fullName() : existing.getFullName();
        String firstName = command.firstName() != null ? command.firstName() : existing.getFirstName();
        String lastName = command.lastName() != null ? command.lastName() : existing.getLastName();

        Patient updated = new Patient(
            new PatientId(command.patientId()),
            fullName,
            firstName,
            lastName,
            command.birthDate() != null ? command.birthDate() : existing.getBirthDate(),
            command.dniNie() != null ? command.dniNie() : existing.getDniNie(),
            command.email() != null ? command.email() : existing.getEmail(),
            command.phone() != null ? command.phone() : existing.getPhone(),
            command.gender() != null ? command.gender() : existing.getGender(),
            existing.getBloodType(),
            command.address() != null ? command.address() : existing.getAddress(),
            command.city() != null ? command.city() : existing.getCity(),
            command.postalCode() != null ? command.postalCode() : existing.getPostalCode(),
            command.notes() != null ? command.notes() : existing.getNotes(),
            existing.isActive(),
            existing.getClinicalAlerts(),
            existing.getClinicId(),
            existing.getCreatedAt()
        );
        return repository.save(updated);
    }
}
