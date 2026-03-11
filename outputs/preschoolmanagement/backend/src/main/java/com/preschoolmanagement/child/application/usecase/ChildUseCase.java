package com.preschoolmanagement.child.application.usecase;

import com.preschoolmanagement.child.domain.repository.ChildRepository;
import java.time.LocalDate;
import java.util.List;



public class ChildUseCase {

    private final ChildRepository repository;

    public ChildUseCase(ChildRepository repository) {
        this.repository = repository;
    }

}
