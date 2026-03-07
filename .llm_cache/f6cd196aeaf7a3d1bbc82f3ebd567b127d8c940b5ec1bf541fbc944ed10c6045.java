package com.preschoolmanagement.child.domain.repository;

import com.preschoolmanagement.child.domain.model.Child;
import com.preschoolmanagement.child.domain.valueobject.ChildId;

import java.util.Optional;

public interface ChildRepository {

    Optional<Child> findById(ChildId id);

    void save(Child entity);
}