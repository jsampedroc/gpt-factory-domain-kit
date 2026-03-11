package com.preschoolmanagement.child.application.usecase;

import com.preschoolmanagement.child.domain.repository.AuthorizedPickupRepository;



public class AuthorizedPickupUseCase {

    private final AuthorizedPickupRepository repository;

    public AuthorizedPickupUseCase(AuthorizedPickupRepository repository) {
        this.repository = repository;
    }

}
