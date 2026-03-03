package com.preschoolmanagement.infrastructure.rest;

import com.preschoolmanagement.application.dto.TeacherRequest;
import com.preschoolmanagement.application.dto.TeacherResponse;
import com.preschoolmanagement.application.mapper.TeacherMapper;
import com.preschoolmanagement.application.service.TeacherService;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/teachers")
public class TeacherController {

    private final TeacherService service;
    private final TeacherMapper mapper;

    public TeacherController(TeacherService service, TeacherMapper mapper) {
        this.service = service;
        this.mapper = mapper;
    }

    @PostMapping
    public void create(@RequestBody TeacherRequest request) {
        service.save(mapper.toDomain(request));
    }

    @GetMapping("/{id}")
    public TeacherResponse get(@PathVariable String id) {
        return mapper.toResponse(
                service.findById(/* convert id */ null)
        );
    }
}
