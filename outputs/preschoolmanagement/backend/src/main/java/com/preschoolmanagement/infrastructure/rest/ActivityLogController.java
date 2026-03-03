package com.preschoolmanagement.infrastructure.rest;

import com.preschoolmanagement.application.dto.ActivityLogRequest;
import com.preschoolmanagement.application.dto.ActivityLogResponse;
import com.preschoolmanagement.application.mapper.ActivityLogMapper;
import com.preschoolmanagement.application.service.ActivityLogService;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/activity-logs")
public class ActivityLogController {

    private final ActivityLogService service;
    private final ActivityLogMapper mapper;

    public ActivityLogController(ActivityLogService service, ActivityLogMapper mapper) {
        this.service = service;
        this.mapper = mapper;
    }

    @PostMapping
    public void create(@RequestBody ActivityLogRequest request) {
        service.save(mapper.toDomain(request));
    }

    @GetMapping("/{id}")
    public ActivityLogResponse get(@PathVariable String id) {
        return mapper.toResponse(
                service.findById(/* convert id */ null)
        );
    }
}
