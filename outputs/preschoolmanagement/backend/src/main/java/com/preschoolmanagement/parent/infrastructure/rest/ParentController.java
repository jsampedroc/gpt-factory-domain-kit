package com.preschoolmanagement.parent.infrastructure.rest;

import java.util.List;



@RestController
@RequestMapping("/parents")
public class ParentController {

    private final ParentUseCase useCase;

    public ParentController(ParentUseCase useCase) {
        this.useCase = useCase;
    }

}
