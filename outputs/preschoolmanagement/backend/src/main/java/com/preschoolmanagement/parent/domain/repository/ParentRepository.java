package com.preschoolmanagement.parent.domain.repository;

import com.preschoolmanagement.parent.domain.model.Parent;
import com.preschoolmanagement.parent.domain.valueobject.ParentId;
import java.util.Optional;



public interface ParentRepository {

    Parent save(Parent entity);

    Optional<Parent> findById(ParentId id);

}
