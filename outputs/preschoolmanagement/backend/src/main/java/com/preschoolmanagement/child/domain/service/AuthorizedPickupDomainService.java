package com.preschoolmanagement.child.domain.service;

import com.preschoolmanagement.child.domain.repository.AuthorizedPickupRepository;



public class AuthorizedPickupDomainService {

    private final AuthorizedPickupRepository repository;

    public AuthorizedPickupDomainService(AuthorizedPickupRepository repository) {
        this.repository = repository;
    }

}
