package com.dentalclinic.appointment.infrastructure.rest;

import com.dentalclinic.appointment.domain.model.Appointment;
import com.dentalclinic.appointment.application.dto.AppointmentResponse;
import com.dentalclinic.appointment.application.usecase.ListAllAppointmentsUseCase;
import com.dentalclinic.appointment.application.usecase.ListAllAppointmentsQuery;
import com.dentalclinic.appointment.application.usecase.GetAppointmentByIdUseCase;
import com.dentalclinic.appointment.application.usecase.GetAppointmentByIdQuery;
import com.dentalclinic.appointment.application.usecase.RegisterAppointmentUseCase;
import com.dentalclinic.appointment.application.usecase.RegisterAppointmentCommand;
import com.dentalclinic.appointment.application.usecase.UpdateAppointmentUseCase;
import com.dentalclinic.appointment.application.usecase.UpdateAppointmentCommand;
import com.dentalclinic.appointment.application.usecase.DeactivateAppointmentUseCase;
import com.dentalclinic.appointment.application.usecase.DeactivateAppointmentCommand;
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

@Tag(name = "Appointments", description = "Gestión de citas")
@SecurityRequirement(name = "bearerAuth")
@RestController
@RequestMapping("/appointments")
@CrossOrigin(origins = "*")
public class AppointmentController {

    private final ListAllAppointmentsUseCase listAll;
    private final GetAppointmentByIdUseCase getById;
    private final RegisterAppointmentUseCase register;
    private final UpdateAppointmentUseCase update;
    private final DeactivateAppointmentUseCase deactivate;

    public AppointmentController(
            ListAllAppointmentsUseCase listAll,
            GetAppointmentByIdUseCase getById,
            RegisterAppointmentUseCase register,
            UpdateAppointmentUseCase update,
            DeactivateAppointmentUseCase deactivate) {
        this.listAll    = listAll;
        this.getById    = getById;
        this.register   = register;
        this.update     = update;
        this.deactivate = deactivate;
    }
    @Operation(summary = "Listar todos (paginado)", description = "Devuelve una página de registros con soporte de búsqueda")

    @GetMapping
    public PageResponse<AppointmentResponse> getAll(
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "20") int size,
            @RequestParam(defaultValue = "") String search) {
        PageResult<Appointment> result = listAll.execute(new ListAllAppointmentsQuery(page, size, search));
        List<AppointmentResponse> content = result.content().stream()
                .map(this::toResponse).collect(Collectors.toList());
        return new PageResponse<>(content, result.page(), result.size(),
                result.total(), result.totalPages(), result.isLast());
    }
    @Operation(summary = "Obtener por ID")

    @GetMapping("/{id}")
    public ResponseEntity<AppointmentResponse> getOne(@PathVariable("id") UUID id) {
        return getById.execute(new GetAppointmentByIdQuery(id))
                .map(this::toResponse)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }
    @Operation(summary = "Crear nuevo registro")

    @PostMapping
    public ResponseEntity<AppointmentResponse> create(@RequestBody @Valid RegisterAppointmentCommand cmd) {
        return ResponseEntity.ok(toResponse(register.execute(cmd)));
    }
    @Operation(summary = "Actualizar registro existente")

    @PutMapping("/{id}")
    public ResponseEntity<AppointmentResponse> updateOne(@PathVariable("id") UUID id,
                                                          @RequestBody @Valid UpdateAppointmentCommand cmd) {
        return ResponseEntity.ok(toResponse(update.execute(cmd)));
    }
    @Operation(summary = "Desactivar registro (soft delete)")

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteOne(@PathVariable("id") UUID id) {
        deactivate.execute(new DeactivateAppointmentCommand(id));
        return ResponseEntity.noContent().build();
    }

    private AppointmentResponse toResponse(Appointment e) {
        return new AppointmentResponse(
                e.getId().value(),
                e.getPatientId(),
                e.getPatientName(),
                e.getPractitionerId(),
                e.getPractitionerName(),
                e.getStartTime() != null ? e.getStartTime().toString() : null,
                e.getEndTime() != null ? e.getEndTime().toString() : null,
                e.getProcedureName(),
                e.getStatus() != null ? e.getStatus().getValue() : null,
                e.getNotes(),
                e.getClinicId(),
                e.getCreatedAt()
        );
    }
}
