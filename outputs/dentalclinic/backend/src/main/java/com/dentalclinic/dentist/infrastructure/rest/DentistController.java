package com.dentalclinic.dentist.infrastructure.rest;

import com.dentalclinic.dentist.domain.model.Dentist;
import com.dentalclinic.dentist.application.dto.DentistResponse;
import com.dentalclinic.dentist.application.usecase.ListAllDentistsUseCase;
import com.dentalclinic.dentist.application.usecase.ListAllDentistsQuery;
import com.dentalclinic.dentist.application.usecase.GetDentistByIdUseCase;
import com.dentalclinic.dentist.application.usecase.GetDentistByIdQuery;
import com.dentalclinic.dentist.application.usecase.RegisterDentistUseCase;
import com.dentalclinic.dentist.application.usecase.RegisterDentistCommand;
import com.dentalclinic.dentist.application.usecase.UpdateDentistUseCase;
import com.dentalclinic.dentist.application.usecase.UpdateDentistCommand;
import com.dentalclinic.dentist.application.usecase.DeactivateDentistUseCase;
import com.dentalclinic.dentist.application.usecase.DeactivateDentistCommand;
import com.dentalclinic.shared.PageResult;
import com.dentalclinic.shared.PageResponse;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.security.SecurityRequirement;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.http.ResponseEntity;
import jakarta.validation.Valid;
import org.springframework.web.bind.annotation.*;
import java.util.List;
import java.util.UUID;
import java.util.stream.Collectors;

@Tag(name = "Dentists", description = "Gestión de dentistas")
@SecurityRequirement(name = "bearerAuth")
@RestController
@RequestMapping("/dentists")
@CrossOrigin(origins = "*")
public class DentistController {

    private final ListAllDentistsUseCase listAll;
    private final GetDentistByIdUseCase getById;
    private final RegisterDentistUseCase register;
    private final UpdateDentistUseCase update;
    private final DeactivateDentistUseCase deactivate;

    public DentistController(
            ListAllDentistsUseCase listAll,
            GetDentistByIdUseCase getById,
            RegisterDentistUseCase register,
            UpdateDentistUseCase update,
            DeactivateDentistUseCase deactivate) {
        this.listAll    = listAll;
        this.getById    = getById;
        this.register   = register;
        this.update     = update;
        this.deactivate = deactivate;
    }
    @Operation(summary = "Listar todos (paginado)", description = "Devuelve una página de registros con soporte de búsqueda")

    @GetMapping
    public PageResponse<DentistResponse> getAll(
            @RequestParam(defaultValue = "0")  int page,
            @RequestParam(defaultValue = "20") int size,
            @RequestParam(defaultValue = "")   String search) {
        PageResult<Dentist> result = listAll.execute(new ListAllDentistsQuery(page, size, search));
        List<DentistResponse> content = result.content().stream()
                .map(this::toResponse).collect(Collectors.toList());
        return new PageResponse<>(content, result.page(), result.size(),
                result.total(), result.totalPages(), result.isLast());
    }
    @Operation(summary = "Obtener por ID")

    @GetMapping("/{id}")
    public ResponseEntity<DentistResponse> getOne(@PathVariable("id") UUID id) {
        return getById.execute(new GetDentistByIdQuery(id))
                .map(this::toResponse)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }
    @Operation(summary = "Crear nuevo registro")

    @PostMapping
    public ResponseEntity<DentistResponse> create(@RequestBody @Valid RegisterDentistCommand cmd) {
        return ResponseEntity.ok(toResponse(register.execute(cmd)));
    }
    @Operation(summary = "Actualizar registro existente")

    @PutMapping("/{id}")
    public ResponseEntity<DentistResponse> updateOne(@PathVariable("id") UUID id,
                                                      @RequestBody @Valid UpdateDentistCommand cmd) {
        return ResponseEntity.ok(toResponse(update.execute(cmd)));
    }
    @Operation(summary = "Desactivar registro (soft delete)")

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteOne(@PathVariable("id") UUID id) {
        deactivate.execute(new DeactivateDentistCommand(id));
        return ResponseEntity.noContent().build();
    }

    private DentistResponse toResponse(Dentist e) {
        return new DentistResponse(
                e.getId().value(),
                e.getFirstName(),
                e.getLastName(),
                e.getLicenseNumber(),
                e.getDentistId()
        );
    }
}
