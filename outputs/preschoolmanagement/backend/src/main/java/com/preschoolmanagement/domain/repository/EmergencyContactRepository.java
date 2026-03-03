package com.preschoolmanagement.domain.repository;

import com.preschoolmanagement.domain.model.EmergencyContact;
import com.preschoolmanagement.domain.valueobject.EmergencyContactId;

import java.util.Optional;

public interface EmergencyContactRepository {

    Optional<EmergencyContact> findById(EmergencyContactId id);

    void save(EmergencyContact entity);
}
