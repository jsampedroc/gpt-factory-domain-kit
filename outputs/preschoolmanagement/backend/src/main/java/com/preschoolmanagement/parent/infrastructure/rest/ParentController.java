package com.preschoolmanagement.parent.infrastructure.rest;

import java.util.List;



@RestController
@RequestMapping("/parents")
public class ParentController {

    private final ParentService service;

    public ParentController(ParentService service) {
        this.service = service;
    }

}
