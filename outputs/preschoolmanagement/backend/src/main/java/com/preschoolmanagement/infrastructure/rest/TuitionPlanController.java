package com.preschoolmanagement.infrastructure.rest;

import com.preschoolmanagement.application.dto.TuitionPlanRequest;
import com.preschoolmanagement.application.dto.TuitionPlanResponse;
import com.preschoolmanagement.application.mapper.TuitionPlanMapper;
import com.preschoolmanagement.application.service.TuitionPlanService;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/tuition-plans")
public class TuitionPlanController {

    private final TuitionPlanService service;
    private final TuitionPlanMapper mapper;

    public TuitionPlanController(TuitionPlanService service, TuitionPlanMapper mapper) {
        this.service = service;
        this.mapper = mapper;
    }

    @PostMapping
    public void create(@RequestBody TuitionPlanRequest request) {
        service.save(mapper.toDomain(request));
    }

    @GetMapping("/{id}")
    public TuitionPlanResponse get(@PathVariable String id) {
        return mapper.toResponse(
                service.findById(/* convert id */ null)
        );
    }
}
