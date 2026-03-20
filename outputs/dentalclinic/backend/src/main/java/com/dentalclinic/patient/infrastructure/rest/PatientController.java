package com.dentalclinic.patient.infrastructure.rest;

import com.dentalclinic.patient.domain.model.Patient;
import com.dentalclinic.patient.application.dto.PatientResponse;
import com.dentalclinic.shared.PageResult;
import com.dentalclinic.shared.PageResponse;
import com.dentalclinic.patient.application.usecase.ListAllPatientsUseCase;
import com.dentalclinic.patient.application.usecase.ListAllPatientsQuery;
import com.dentalclinic.patient.application.usecase.GetPatientByIdUseCase;
import com.dentalclinic.patient.application.usecase.GetPatientByIdQuery;
import com.dentalclinic.patient.application.usecase.RegisterPatientUseCase;
import com.dentalclinic.patient.application.usecase.RegisterPatientCommand;
import com.dentalclinic.patient.application.usecase.UpdatePatientUseCase;
import com.dentalclinic.patient.application.usecase.UpdatePatientCommand;
import com.dentalclinic.patient.application.usecase.DeactivatePatientUseCase;
import com.dentalclinic.patient.application.usecase.DeactivatePatientCommand;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.security.SecurityRequirement;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.http.ResponseEntity;
import jakarta.validation.Valid;
import org.springframework.web.bind.annotation.*;
import java.util.List;
import java.util.UUID;
import java.util.stream.Collectors;

@Tag(name = "Patients", description = "Gestión de pacientes")
@SecurityRequirement(name = "bearerAuth")
@RestController
@RequestMapping("/patients")
@CrossOrigin(origins = "*")
public class PatientController {

    private final ListAllPatientsUseCase listAll;
    private final GetPatientByIdUseCase getById;
    private final RegisterPatientUseCase register;
    private final UpdatePatientUseCase update;
    private final DeactivatePatientUseCase deactivate;

    public PatientController(
            ListAllPatientsUseCase listAll,
            GetPatientByIdUseCase getById,
            RegisterPatientUseCase register,
            UpdatePatientUseCase update,
            DeactivatePatientUseCase deactivate) {
        this.listAll    = listAll;
        this.getById    = getById;
        this.register   = register;
        this.update     = update;
        this.deactivate = deactivate;
    }
    @Operation(summary = "Listar todos (paginado)", description = "Devuelve una página de registros con soporte de búsqueda")

    @GetMapping
    public PageResponse<PatientResponse> getAll(
            @RequestParam(defaultValue = "0")  int page,
            @RequestParam(defaultValue = "20") int size,
            @RequestParam(defaultValue = "")   String search) {
        PageResult<Patient> result = listAll.execute(new ListAllPatientsQuery(page, size, search));
        List<PatientResponse> content = result.content().stream()
                .map(this::toResponse).collect(Collectors.toList());
        return new PageResponse<>(content, result.page(), result.size(),
                result.total(), result.totalPages(), result.isLast());
    }
    @Operation(summary = "Obtener por ID")

    @GetMapping("/{id}")
    public ResponseEntity<PatientResponse> getOne(@PathVariable("id") UUID id) {
        return getById.execute(new GetPatientByIdQuery(id))
                .map(this::toResponse)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }
    @Operation(summary = "Crear nuevo registro")

    @PostMapping
    public ResponseEntity<PatientResponse> create(@RequestBody @Valid RegisterPatientCommand cmd) {
        return ResponseEntity.ok(toResponse(register.execute(cmd)));
    }
    @Operation(summary = "Actualizar registro existente")

    @PutMapping("/{id}")
    public ResponseEntity<PatientResponse> updateOne(@PathVariable("id") UUID id,
                                                      @RequestBody @Valid UpdatePatientCommand cmd) {
        return ResponseEntity.ok(toResponse(update.execute(cmd)));
    }
    @Operation(summary = "Desactivar registro (soft delete)")

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteOne(@PathVariable("id") UUID id) {
        deactivate.execute(new DeactivatePatientCommand(id));
        return ResponseEntity.noContent().build();
    }

    private PatientResponse toResponse(Patient e) {
        return new PatientResponse(
                e.getId().value(),
                e.getFullName(),
                e.getFirstName(),
                e.getLastName(),
                e.getBirthDate() != null ? e.getBirthDate().toString() : null,
                e.getDniNie(),
                e.getEmail(),
                e.getPhone(),
                e.getGender(),
                e.getBloodType(),
                e.getAddress(),
                e.getCity(),
                e.getPostalCode(),
                e.getNotes(),
                e.isActive(),
                e.getClinicalAlerts(),
                e.getCreatedAt()
        );
    }
}
