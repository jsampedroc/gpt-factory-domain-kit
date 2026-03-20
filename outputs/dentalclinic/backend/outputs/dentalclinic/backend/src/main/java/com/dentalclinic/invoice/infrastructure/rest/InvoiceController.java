package com.dentalclinic.invoice.infrastructure.rest;

import com.dentalclinic.invoice.domain.model.Invoice;
import com.dentalclinic.invoice.application.usecase.ListAllInvoicesUseCase;
import com.dentalclinic.invoice.application.usecase.ListAllInvoicesQuery;
import com.dentalclinic.invoice.application.usecase.GetInvoiceByIdUseCase;
import com.dentalclinic.invoice.application.usecase.GetInvoiceByIdQuery;
import com.dentalclinic.invoice.application.usecase.RegisterInvoiceUseCase;
import com.dentalclinic.invoice.application.usecase.RegisterInvoiceCommand;
import com.dentalclinic.invoice.application.usecase.UpdateInvoiceUseCase;
import com.dentalclinic.invoice.application.usecase.UpdateInvoiceCommand;
import com.dentalclinic.invoice.application.usecase.DeactivateInvoiceUseCase;
import com.dentalclinic.invoice.application.usecase.DeactivateInvoiceCommand;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import java.util.List;
import java.util.UUID;
import java.util.stream.Collectors;

@RestController
@RequestMapping("/invoices")
@CrossOrigin(origins = "*")
public class InvoiceController {

    private final ListAllInvoicesUseCase listAll;
    private final GetInvoiceByIdUseCase  getById;
    private final RegisterInvoiceUseCase register;
    private final UpdateInvoiceUseCase   update;
    private final DeactivateInvoiceUseCase deactivate;

    public InvoiceController(
            ListAllInvoicesUseCase listAll,
            GetInvoiceByIdUseCase  getById,
            RegisterInvoiceUseCase register,
            UpdateInvoiceUseCase   update,
            DeactivateInvoiceUseCase deactivate) {
        this.listAll    = listAll;
        this.getById    = getById;
        this.register   = register;
        this.update     = update;
        this.deactivate = deactivate;
    }

    @GetMapping
    public List<InvoiceResponse> getAll() {
        return listAll.execute(new ListAllInvoicesQuery())
                .stream().map(this::toResponse).collect(Collectors.toList());
    }

    @GetMapping("/{id}")
    public ResponseEntity<InvoiceResponse> getOne(@PathVariable UUID id) {
        return getById.execute(new GetInvoiceByIdQuery(id))
                .map(this::toResponse)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    @PostMapping
    public ResponseEntity<InvoiceResponse> create(@RequestBody RegisterInvoiceCommand cmd) {
        return ResponseEntity.ok(toResponse(register.execute(cmd)));
    }

    @PutMapping("/{id}")
    public ResponseEntity<InvoiceResponse> updateOne(
            @PathVariable UUID id,
            @RequestBody UpdateInvoiceBody body) {
        return ResponseEntity.ok(toResponse(update.execute(new UpdateInvoiceCommand(id, body.patientId() != null ? UUID.fromString(body.patientId()) : null, body.amount(), body.status(), body.issueDate()))));
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteOne(@PathVariable UUID id) {
        deactivate.execute(new DeactivateInvoiceCommand(id));
        return ResponseEntity.noContent().build();
    }

    private InvoiceResponse toResponse(Invoice e) {
        return new InvoiceResponse(
                e.getId().value(),
                e.getPatientId() != null ? e.getPatientId().toString() : null,
                e.getAmount() != null ? e.getAmount().getAmount() : null,
                e.getStatus() != null ? e.getStatus().getValue() : null,
                e.getIssueDate() != null ? e.getIssueDate().toString() : null
        );
    }
}
