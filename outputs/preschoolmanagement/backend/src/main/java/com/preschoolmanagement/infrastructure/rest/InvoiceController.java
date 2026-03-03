package com.preschoolmanagement.infrastructure.rest;

import com.preschoolmanagement.application.dto.InvoiceRequest;
import com.preschoolmanagement.application.dto.InvoiceResponse;
import com.preschoolmanagement.application.mapper.InvoiceMapper;
import com.preschoolmanagement.application.service.InvoiceService;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/invoices")
public class InvoiceController {

    private final InvoiceService service;
    private final InvoiceMapper mapper;

    public InvoiceController(InvoiceService service, InvoiceMapper mapper) {
        this.service = service;
        this.mapper = mapper;
    }

    @PostMapping
    public void create(@RequestBody InvoiceRequest request) {
        service.save(mapper.toDomain(request));
    }

    @GetMapping("/{id}")
    public InvoiceResponse get(@PathVariable String id) {
        return mapper.toResponse(
                service.findById(/* convert id */ null)
        );
    }
}
