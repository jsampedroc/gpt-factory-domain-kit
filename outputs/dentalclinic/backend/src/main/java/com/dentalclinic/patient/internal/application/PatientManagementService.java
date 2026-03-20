package com.dentalclinic.patient.internal.application;

import com.dentalclinic.patient.PatientEvents;
import com.dentalclinic.patient.api.*;
import com.dentalclinic.patient.domain.Patient;
import com.dentalclinic.patient.domain.PatientRepository;
import com.dentalclinic.shared.events.DomainEventPublisher;
import jakarta.persistence.EntityNotFoundException;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.Optional;
import java.util.UUID;
import java.util.stream.Collectors;

@Service
@Transactional
class PatientManagementService implements PatientService {

    private final PatientRepository repository;
    private final DomainEventPublisher eventPublisher;

    PatientManagementService(PatientRepository repository, DomainEventPublisher eventPublisher) {
        this.repository = repository;
        this.eventPublisher = eventPublisher;
    }

    @Override
    public PatientDto create(CreatePatientRequest request, UUID clinicId) {
        Patient patient = new Patient(request.fullName(), request.email(), request.phone(), clinicId);
        patient.setFirstName(request.firstName());
        patient.setLastName(request.lastName());
        patient.setBirthDate(request.birthDate());
        patient.setDniNie(request.dniNie());
        patient.setGender(request.gender());
        patient.setBloodType(request.bloodType());
        patient.setAddress(request.address());
        patient.setCity(request.city());
        patient.setPostalCode(request.postalCode());
        patient.setNotes(request.notes());
        Patient saved = repository.save(patient);
        eventPublisher.publish(new PatientEvents.PatientCreated(saved.getId(), clinicId, saved.getFullName()));
        return toDto(saved);
    }

    @Override
    @Transactional(readOnly = true)
    public Optional<PatientDto> findById(UUID id, UUID clinicId) {
        return repository.findByIdAndClinicId(id, clinicId).map(this::toDto);
    }

    @Override
    @Transactional(readOnly = true)
    public List<PatientDto> findAll(UUID clinicId) {
        return repository.findByClinicIdAndDeletedFalse(clinicId).stream().map(this::toDto).collect(Collectors.toList());
    }

    @Override
    @Transactional(readOnly = true)
    public List<PatientDto> search(UUID clinicId, String query) {
        return repository.search(clinicId, query).stream().map(this::toDto).collect(Collectors.toList());
    }

    @Override
    public PatientDto update(UUID id, UpdatePatientRequest request, UUID clinicId) {
        Patient patient = repository.findByIdAndClinicId(id, clinicId)
                .orElseThrow(() -> new EntityNotFoundException("Patient not found: " + id));
        if (request.fullName() != null) patient.setFullName(request.fullName());
        if (request.firstName() != null) patient.setFirstName(request.firstName());
        if (request.lastName() != null) patient.setLastName(request.lastName());
        if (request.birthDate() != null) patient.setBirthDate(request.birthDate());
        if (request.dniNie() != null) patient.setDniNie(request.dniNie());
        if (request.email() != null) patient.setEmail(request.email());
        if (request.phone() != null) patient.setPhone(request.phone());
        if (request.gender() != null) patient.setGender(request.gender());
        if (request.bloodType() != null) patient.setBloodType(request.bloodType());
        if (request.address() != null) patient.setAddress(request.address());
        if (request.city() != null) patient.setCity(request.city());
        if (request.postalCode() != null) patient.setPostalCode(request.postalCode());
        if (request.notes() != null) patient.setNotes(request.notes());
        if (request.clinicalAlerts() != null) patient.setClinicalAlerts(request.clinicalAlerts());
        patient.setActive(request.active());
        Patient saved = repository.save(patient);
        eventPublisher.publish(new PatientEvents.PatientUpdated(saved.getId(), clinicId));
        return toDto(saved);
    }

    @Override
    public void delete(UUID id, UUID clinicId) {
        Patient patient = repository.findByIdAndClinicId(id, clinicId)
                .orElseThrow(() -> new EntityNotFoundException("Patient not found: " + id));
        patient.setDeleted(true);
        repository.save(patient);
    }

    @Override
    @Transactional(readOnly = true)
    public long count(UUID clinicId) {
        return repository.countByClinicIdAndDeletedFalse(clinicId);
    }

    private PatientDto toDto(Patient p) {
        return new PatientDto(p.getId(), p.getClinicId(), p.getFullName(), p.getFirstName(), p.getLastName(),
                p.getBirthDate(), p.getDniNie(), p.getEmail(), p.getPhone(), p.getGender(), p.getBloodType(),
                p.getAddress(), p.getCity(), p.getPostalCode(), p.getNotes(), p.isActive(),
                p.getClinicalAlerts(), p.getCreatedAt(), p.getUpdatedAt());
    }
}
