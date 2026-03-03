package com.preschoolmanagement.infrastructure.rest;

import com.preschoolmanagement.application.dto.EmergencyContactRequest;
import com.preschoolmanagement.application.dto.EmergencyContactResponse;
import com.preschoolmanagement.application.mapper.EmergencyContactMapper;
import com.preschoolmanagement.application.service.EmergencyContactService;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/emergency-contacts")
public class EmergencyContactController {

    private final EmergencyContactService service;
    private final EmergencyContactMapper mapper;

    public EmergencyContactController(EmergencyContactService service, EmergencyContactMapper mapper) {
        this.service = service;
        this.mapper = mapper;
    }

    @PostMapping
    public void create(@RequestBody EmergencyContactRequest request) {
        service.save(mapper.toDomain(request));
    }

    @GetMapping("/{id}")
    public EmergencyContactResponse get(@PathVariable String id) {
        return mapper.toResponse(
                service.findById(/* convert id */ null)
        );
    }
}
