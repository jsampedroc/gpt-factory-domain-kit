package com.preschoolmanagement.child.application.dto;

import com.preschoolmanagement.child.domain.valueobject.AuthorizedPickupRequestId;



public record AuthorizedPickupRequest(
        AuthorizedPickupRequestId id,
        String firstName,
        String lastName,
        String relationship,
        String contactNumber
) {}
