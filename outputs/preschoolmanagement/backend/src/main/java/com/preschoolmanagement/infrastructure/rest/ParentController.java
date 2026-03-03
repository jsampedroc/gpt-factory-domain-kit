package com.preschoolmanagement.infrastructure.rest;

import com.preschoolmanagement.application.dto.ParentRequest;
import com.preschoolmanagement.application.dto.ParentResponse;
import com.preschoolmanagement.application.mapper.ParentMapper;
import com.preschoolmanagement.application.service.ParentService;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/parents")
public class ParentController {

    private final ParentService service;
    private final ParentMapper mapper;

    public ParentController(ParentService service, ParentMapper mapper) {
        this.service = service;
        this.mapper = mapper;
    }

    @PostMapping
    public void create(@RequestBody ParentRequest request) {
        service.save(mapper.toDomain(request));
    }

    @GetMapping("/{id}")
    public ParentResponse get(@PathVariable String id) {
        return mapper.toResponse(
                service.findById(/* convert id */ null)
        );
    }
}
