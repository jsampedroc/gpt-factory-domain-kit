package com.preschoolmanagement.child.domain.repository;

import com.preschoolmanagement.child.domain.model.Immunization;
import com.preschoolmanagement.child.domain.valueobject.ImmunizationId;

import java.util.Optional;

public interface ImmunizationRepository {

    Optional<Immunization> findById(ImmunizationId id);

    void save(Immunization entity);
}