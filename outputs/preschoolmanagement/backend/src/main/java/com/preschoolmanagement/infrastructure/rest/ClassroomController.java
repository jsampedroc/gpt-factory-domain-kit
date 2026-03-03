package com.preschoolmanagement.infrastructure.rest;

import com.preschoolmanagement.application.dto.ClassroomRequest;
import com.preschoolmanagement.application.dto.ClassroomResponse;
import com.preschoolmanagement.application.mapper.ClassroomMapper;
import com.preschoolmanagement.application.service.ClassroomService;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/classrooms")
public class ClassroomController {

    private final ClassroomService service;
    private final ClassroomMapper mapper;

    public ClassroomController(ClassroomService service, ClassroomMapper mapper) {
        this.service = service;
        this.mapper = mapper;
    }

    @PostMapping
    public void create(@RequestBody ClassroomRequest request) {
        service.save(mapper.toDomain(request));
    }

    @GetMapping("/{id}")
    public ClassroomResponse get(@PathVariable String id) {
        return mapper.toResponse(
                service.findById(/* convert id */ null)
        );
    }
}
