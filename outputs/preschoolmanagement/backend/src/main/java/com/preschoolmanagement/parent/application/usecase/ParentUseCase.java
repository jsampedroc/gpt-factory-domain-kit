package com.preschoolmanagement.parent.application.usecase;

import com.preschoolmanagement.parent.domain.repository.ParentRepository;
import java.util.List;



public class ParentUseCase {

    private final ParentRepository repository;

    public ParentUseCase(ParentRepository repository) {
        this.repository = repository;
    }

}
