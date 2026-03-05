package com.preschoolmanagement.domain.repository;

import com.preschoolmanagement.domain.model.Parent;
import com.preschoolmanagement.domain.valueobject.ParentId;

import java.util.Optional;

public interface ParentRepository {

    Optional<Parent> findById(ParentId id);

    void save(Parent entity);
}