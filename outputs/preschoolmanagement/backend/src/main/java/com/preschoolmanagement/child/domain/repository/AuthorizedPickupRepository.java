package com.preschoolmanagement.child.domain.repository;

import com.preschoolmanagement.child.domain.model.AuthorizedPickup;
import com.preschoolmanagement.child.domain.valueobject.AuthorizedPickupId;
import java.util.Optional;



public interface AuthorizedPickupRepository {

    AuthorizedPickup save(AuthorizedPickup entity);

    Optional<AuthorizedPickup> findById(AuthorizedPickupId id);

}
