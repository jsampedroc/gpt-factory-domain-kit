package com.preschoolmanagement.child.infrastructure.rest;

import java.time.LocalDate;
import java.util.List;



@RestController
@RequestMapping("/childs")
public class ChildController {

    private final ChildService service;

    public ChildController(ChildService service) {
        this.service = service;
    }

}
