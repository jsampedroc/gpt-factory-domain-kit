package com.dentalclinic.treatment.infrastructure.rest;

import com.dentalclinic.shared.PageResponse;
import com.dentalclinic.shared.PageResult;
import com.dentalclinic.treatment.domain.model.Treatment;
import com.dentalclinic.treatment.application.dto.TreatmentResponse;
import com.dentalclinic.treatment.application.usecase.ListAllTreatmentsUseCase;
import com.dentalclinic.treatment.application.usecase.ListAllTreatmentsQuery;
import com.dentalclinic.treatment.application.usecase.GetTreatmentByIdUseCase;
import com.dentalclinic.treatment.application.usecase.GetTreatmentByIdQuery;
import com.dentalclinic.treatment.application.usecase.RegisterTreatmentUseCase;
import com.dentalclinic.treatment.application.usecase.RegisterTreatmentCommand;
import com.dentalclinic.treatment.application.usecase.UpdateTreatmentUseCase;
import com.dentalclinic.treatment.application.usecase.UpdateTreatmentCommand;
import com.dentalclinic.treatment.application.usecase.DeactivateTreatmentUseCase;
import com.dentalclinic.treatment.application.usecase.DeactivateTreatmentCommand;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.security.SecurityRequirement;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.http.ResponseEntity;
import jakarta.validation.Valid;
import org.springframework.web.bind.annotation.*;
import java.util.UUID;
import java.util.stream.Collectors;

@Tag(name = "Treatments", description = "Gestión de tratamientos")
@SecurityRequirement(name = "bearerAuth")
@RestController
@RequestMapping("/treatments")
@CrossOrigin(origins = "*")
public class TreatmentController {

    private final ListAllTreatmentsUseCase listAll;
    private final GetTreatmentByIdUseCase getById;
    private final RegisterTreatmentUseCase register;
    private final UpdateTreatmentUseCase update;
    private final DeactivateTreatmentUseCase deactivate;

    public TreatmentController(
            ListAllTreatmentsUseCase listAll,
            GetTreatmentByIdUseCase getById,
            RegisterTreatmentUseCase register,
            UpdateTreatmentUseCase update,
            DeactivateTreatmentUseCase deactivate) {
        this.listAll    = listAll;
        this.getById    = getById;
        this.register   = register;
        this.update     = update;
        this.deactivate = deactivate;
    }
    @Operation(summary = "Listar todos (paginado)", description = "Devuelve una página de registros con soporte de búsqueda")

    @GetMapping
    public PageResponse<TreatmentResponse> getAll(
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "20") int size,
            @RequestParam(required = false) String search) {
        PageResult<Treatment> result = listAll.execute(new ListAllTreatmentsQuery(page, size, search));
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
    public ResponseEntity<TreatmentResponse> getOne(@PathVariable("id") UUID id) {
        return getById.execute(new GetTreatmentByIdQuery(id))
                .map(this::toResponse)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }
    @Operation(summary = "Crear nuevo registro")

    @PostMapping
    public ResponseEntity<TreatmentResponse> create(@RequestBody @Valid RegisterTreatmentCommand cmd) {
        return ResponseEntity.ok(toResponse(register.execute(cmd)));
    }
    @Operation(summary = "Actualizar registro existente")

    @PutMapping("/{id}")
    public ResponseEntity<TreatmentResponse> updateOne(@PathVariable("id") UUID id,
                                                        @RequestBody @Valid UpdateTreatmentCommand cmd) {
        return ResponseEntity.ok(toResponse(update.execute(cmd)));
    }
    @Operation(summary = "Desactivar registro (soft delete)")

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteOne(@PathVariable("id") UUID id) {
        deactivate.execute(new DeactivateTreatmentCommand(id));
        return ResponseEntity.noContent().build();
    }

    private TreatmentResponse toResponse(Treatment e) {
        return new TreatmentResponse(
                e.getId().value(),
                e.getTreatmentId(),
                e.getAppointmentId(),
                e.getDescription(),
                e.getCost() != null ? e.getCost().getAmount() : null
        );
    }
}
