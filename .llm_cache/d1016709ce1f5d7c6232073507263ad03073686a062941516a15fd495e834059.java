package com.preschoolmanagement.child.application.mapper;

import com.preschoolmanagement.child.application.dto.AuthorizedPickupRequest;
import com.preschoolmanagement.child.application.dto.AuthorizedPickupResponse;
import com.preschoolmanagement.child.domain.model.AuthorizedPickup;
import org.mapstruct.Mapper;

@Mapper
public interface AuthorizedPickupMapper {

    AuthorizedPickup toDomain(AuthorizedPickupRequest request);

    AuthorizedPickupResponse toResponse(AuthorizedPickup authorizedPickup);
}