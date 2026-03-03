package com.preschoolmanagement.application.service;

import com.preschoolmanagement.domain.model.EmergencyContact;
import com.preschoolmanagement.domain.repository.EmergencyContactRepository;
import com.preschoolmanagement.domain.valueobject.EmergencyContactId;

public class EmergencyContactService {

    private final EmergencyContactRepository repository;

    public EmergencyContactService(EmergencyContactRepository repository) {
        this.repository = repository;
    }

    public EmergencyContact findById(EmergencyContactId id) {
        return repository.findById(id)
                .orElseThrow(() -> new IllegalArgumentException("EmergencyContact not found"));
    }

    public void save(EmergencyContact emergencyContact) {
        repository.save(emergencyContact);
    }
}
