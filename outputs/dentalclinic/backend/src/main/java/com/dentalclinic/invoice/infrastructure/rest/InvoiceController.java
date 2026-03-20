package com.dentalclinic.invoice.infrastructure.rest;

import com.dentalclinic.shared.PageResponse;
import com.dentalclinic.shared.PageResult;
import com.dentalclinic.invoice.domain.model.Invoice;
import com.dentalclinic.invoice.application.dto.InvoiceResponse;
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
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.security.SecurityRequirement;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.http.ResponseEntity;
import jakarta.validation.Valid;
import org.springframework.web.bind.annotation.*;
import java.util.UUID;
import java.util.stream.Collectors;

@Tag(name = "Invoices", description = "Gestión de facturas")
@SecurityRequirement(name = "bearerAuth")
@RestController
@RequestMapping("/invoices")
@CrossOrigin(origins = "*")
public class InvoiceController {

    private final ListAllInvoicesUseCase listAll;
    private final GetInvoiceByIdUseCase getById;
    private final RegisterInvoiceUseCase register;
    private final UpdateInvoiceUseCase update;
    private final DeactivateInvoiceUseCase deactivate;

    public InvoiceController(
            ListAllInvoicesUseCase listAll,
            GetInvoiceByIdUseCase getById,
            RegisterInvoiceUseCase register,
            UpdateInvoiceUseCase update,
            DeactivateInvoiceUseCase deactivate) {
        this.listAll    = listAll;
        this.getById    = getById;
        this.register   = register;
        this.update     = update;
        this.deactivate = deactivate;
    }
    @Operation(summary = "Listar todos (paginado)", description = "Devuelve una página de registros con soporte de búsqueda")

    @GetMapping
    public PageResponse<InvoiceResponse> getAll(
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "20") int size,
            @RequestParam(required = false) String search) {
        PageResult<Invoice> result = listAll.execute(new ListAllInvoicesQuery(page, size, search));
        return new PageResponse<>(
                result.content().stream().map(this::toResponse).collect(Collectors.toList()),
                result.page(),
                result.size(),
                result.total(),
                result.totalPages(),
                result.isLast()
        );
    }
    @Operation(summary = "Obtener por ID")

    @GetMapping("/{id}")
    public ResponseEntity<InvoiceResponse> getOne(@PathVariable("id") UUID id) {
        return getById.execute(new GetInvoiceByIdQuery(id))
                .map(this::toResponse)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }
    @Operation(summary = "Crear nuevo registro")

    @PostMapping
    public ResponseEntity<InvoiceResponse> create(@RequestBody @Valid RegisterInvoiceCommand cmd) {
        return ResponseEntity.ok(toResponse(register.execute(cmd)));
    }
    @Operation(summary = "Actualizar registro existente")

    @PutMapping("/{id}")
    public ResponseEntity<InvoiceResponse> updateOne(@PathVariable("id") UUID id,
                                                      @RequestBody @Valid UpdateInvoiceCommand cmd) {
        return ResponseEntity.ok(toResponse(update.execute(cmd)));
    }
    @Operation(summary = "Desactivar registro (soft delete)")

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteOne(@PathVariable("id") UUID id) {
        deactivate.execute(new DeactivateInvoiceCommand(id));
        return ResponseEntity.noContent().build();
    }

    private InvoiceResponse toResponse(Invoice e) {
        return new InvoiceResponse(
                e.getId().value(),
                e.getInvoiceId(),
                e.getPatientId(),
                e.getAmount() != null ? e.getAmount().getAmount() : null,
                e.getStatus() != null ? e.getStatus().getValue() : null,
                e.getIssueDate() != null ? e.getIssueDate().toString() : null
        );
    }
}
