package com.preschoolmanagement.parent.domain.service;

import com.preschoolmanagement.parent.domain.repository.ParentRepository;
import java.util.List;



public class ParentDomainService {

    private final ParentRepository repository;

    public ParentDomainService(ParentRepository repository) {
        this.repository = repository;
    }

}
