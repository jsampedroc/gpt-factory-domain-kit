package com.preschoolmanagement.child.application.dto;

public record AuthorizedPickupResponse(
        String firstName,
        String lastName,
        String relationshipToChild
) {}
