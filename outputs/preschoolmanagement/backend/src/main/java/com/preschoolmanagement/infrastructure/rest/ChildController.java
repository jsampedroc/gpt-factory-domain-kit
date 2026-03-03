package com.preschoolmanagement.infrastructure.rest;

import com.preschoolmanagement.application.dto.ChildRequest;
import com.preschoolmanagement.application.dto.ChildResponse;
import com.preschoolmanagement.application.mapper.ChildMapper;
import com.preschoolmanagement.application.service.ChildService;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/children")
public class ChildController {

    private final ChildService service;
    private final ChildMapper mapper;

    public ChildController(ChildService service, ChildMapper mapper) {
        this.service = service;
        this.mapper = mapper;
    }

    @PostMapping
    public void create(@RequestBody ChildRequest request) {
        service.save(mapper.toDomain(request));
    }

    @GetMapping("/{id}")
    public ChildResponse get(@PathVariable String id) {
        return mapper.toResponse(
                service.findById(/* convert id */ null)
        );
    }
}
