package com.preschoolmanagement.child.shared.application.mapper;

import com.preschoolmanagement.child.shared.application.dto.AuthorizedPickupRequest;
import com.preschoolmanagement.child.shared.application.dto.AuthorizedPickupResponse;
import com.preschoolmanagement.child.domain.model.AuthorizedPickup;
import org.mapstruct.Mapper;

@Mapper
public interface AuthorizedPickupMapper {

    AuthorizedPickup toDomain(AuthorizedPickupRequest request);

    AuthorizedPickupResponse toResponse(AuthorizedPickup authorizedPickup);
}