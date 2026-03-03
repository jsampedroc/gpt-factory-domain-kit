package com.preschoolmanagement.domain.repository;

import com.preschoolmanagement.domain.model.Child;
import com.preschoolmanagement.domain.valueobject.ChildId;

import java.util.Optional;

public interface ChildRepository {

    Optional<Child> findById(ChildId id);

    void save(Child entity);
}
