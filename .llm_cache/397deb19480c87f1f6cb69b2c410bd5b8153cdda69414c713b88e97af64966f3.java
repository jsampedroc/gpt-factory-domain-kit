package com.preschoolmanagement.child.domain.repository;

import com.preschoolmanagement.child.domain.model.Allergy;
import com.preschoolmanagement.child.domain.valueobject.AllergyId;

import java.util.Optional;

public interface AllergyRepository {

    Optional<Allergy> findById(AllergyId id);

    void save(Allergy entity);
}