package com.preschoolmanagement.child.domain.service;

import com.preschoolmanagement.child.domain.repository.ChildRepository;
import java.time.LocalDate;
import java.util.List;



public class ChildDomainService {

    private final ChildRepository repository;

    public ChildDomainService(ChildRepository repository) {
        this.repository = repository;
    }

}
