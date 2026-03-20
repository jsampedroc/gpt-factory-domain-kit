package com.dentalclinic.treatment.infrastructure.rest;

import com.dentalclinic.treatment.domain.model.Treatment;
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
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import java.util.List;
import java.util.UUID;
import java.util.stream.Collectors;

@RestController
@RequestMapping("/treatments")
@CrossOrigin(origins = "*")
public class TreatmentController {

    private final ListAllTreatmentsUseCase listAll;
    private final GetTreatmentByIdUseCase  getById;
    private final RegisterTreatmentUseCase register;
    private final UpdateTreatmentUseCase   update;
    private final DeactivateTreatmentUseCase deactivate;

    public TreatmentController(
            ListAllTreatmentsUseCase listAll,
            GetTreatmentByIdUseCase  getById,
            RegisterTreatmentUseCase register,
            UpdateTreatmentUseCase   update,
            DeactivateTreatmentUseCase deactivate) {
        this.listAll    = listAll;
        this.getById    = getById;
        this.register   = register;
        this.update     = update;
        this.deactivate = deactivate;
    }

    @GetMapping
    public List<TreatmentResponse> getAll() {
        return listAll.execute(new ListAllTreatmentsQuery())
                .stream().map(this::toResponse).collect(Collectors.toList());
    }

    @GetMapping("/{id}")
    public ResponseEntity<TreatmentResponse> getOne(@PathVariable UUID id) {
        return getById.execute(new GetTreatmentByIdQuery(id))
                .map(this::toResponse)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    @PostMapping
    public ResponseEntity<TreatmentResponse> create(@RequestBody RegisterTreatmentCommand cmd) {
        return ResponseEntity.ok(toResponse(register.execute(cmd)));
    }

    @PutMapping("/{id}")
    public ResponseEntity<TreatmentResponse> updateOne(
            @PathVariable UUID id,
            @RequestBody UpdateTreatmentBody body) {
        return ResponseEntity.ok(toResponse(update.execute(new UpdateTreatmentCommand(id, body.appointmentId() != null ? UUID.fromString(body.appointmentId()) : null, body.description(), body.cost()))));
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteOne(@PathVariable UUID id) {
        deactivate.execute(new DeactivateTreatmentCommand(id));
        return ResponseEntity.noContent().build();
    }

    private TreatmentResponse toResponse(Treatment e) {
        return new TreatmentResponse(
                e.getId().value(),
                e.getAppointmentId() != null ? e.getAppointmentId().toString() : null,
                e.getDescription(),
                e.getCost() != null ? e.getCost().getAmount() : null
        );
    }
}
