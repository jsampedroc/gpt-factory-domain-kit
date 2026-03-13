package com.preschoolmanagement.child.infrastructure.rest;

import java.time.LocalDate;
import java.util.List;



@RestController
@RequestMapping("/childs")
public class ChildController {

    private final ChildUseCase useCase;

    public ChildController(ChildUseCase useCase) {
        this.useCase = useCase;
    }

}
