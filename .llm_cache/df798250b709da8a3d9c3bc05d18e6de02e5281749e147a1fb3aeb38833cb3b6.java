package com.preschoolmanagement.application.mapper;

import com.preschoolmanagement.application.dto.AuthorizedPickupRequest;
import com.preschoolmanagement.application.dto.AuthorizedPickupResponse;
import com.preschoolmanagement.domain.model.AuthorizedPickup;
import org.mapstruct.Mapper;

@Mapper
public interface AuthorizedPickupMapper {

    AuthorizedPickup toDomain(AuthorizedPickupRequest request);

    AuthorizedPickupResponse toResponse(AuthorizedPickup authorizedPickup);
}