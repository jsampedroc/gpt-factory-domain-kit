package com.preschoolmanagement.child.application.dto;

import com.preschoolmanagement.child.domain.valueobject.AuthorizedPickupResponseId;



public record AuthorizedPickupResponse(
        AuthorizedPickupResponseId id,
        String firstName,
        String lastName,
        String relationship,
        String contactNumber
) {}
