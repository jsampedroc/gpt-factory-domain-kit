package com.example.infrastructure.rest;

import com.example.application.dto.ExampleRequest;
import com.example.application.dto.ExampleResponse;
import com.example.application.mapper.ExampleMapper;
import com.example.application.service.ExampleService;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/examples")
public class ExampleController {

    private final ExampleService service;
    private final ExampleMapper mapper;

    public ExampleController(ExampleService service, ExampleMapper mapper) {
        this.service = service;
        this.mapper = mapper;
    }

    @PostMapping
    public void create(@RequestBody ExampleRequest request) {
        service.save(mapper.toDomain(request));
    }

    @GetMapping("/{id}")
    public ExampleResponse get(@PathVariable String id) {
        return mapper.toResponse(
                service.findById(/* convert id */ null)
        );
    }
}