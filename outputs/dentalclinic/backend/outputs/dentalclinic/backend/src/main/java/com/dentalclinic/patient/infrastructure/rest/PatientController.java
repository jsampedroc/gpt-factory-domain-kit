package com.dentalclinic.patient.infrastructure.rest;

import com.dentalclinic.patient.domain.model.Patient;
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
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import java.util.List;
import java.util.UUID;
import java.util.stream.Collectors;

@RestController
@RequestMapping("/patients")
@CrossOrigin(origins = "*")
public class PatientController {

    private final ListAllPatientsUseCase listAll;
    private final GetPatientByIdUseCase  getById;
    private final RegisterPatientUseCase register;
    private final UpdatePatientUseCase   update;
    private final DeactivatePatientUseCase deactivate;

    public PatientController(
            ListAllPatientsUseCase listAll,
            GetPatientByIdUseCase  getById,
            RegisterPatientUseCase register,
            UpdatePatientUseCase   update,
            DeactivatePatientUseCase deactivate) {
        this.listAll    = listAll;
        this.getById    = getById;
        this.register   = register;
        this.update     = update;
        this.deactivate = deactivate;
    }

    @GetMapping
    public List<PatientResponse> getAll() {
        return listAll.execute(new ListAllPatientsQuery())
                .stream().map(this::toResponse).collect(Collectors.toList());
    }

    @GetMapping("/{id}")
    public ResponseEntity<PatientResponse> getOne(@PathVariable UUID id) {
        return getById.execute(new GetPatientByIdQuery(id))
                .map(this::toResponse)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    @PostMapping
    public ResponseEntity<PatientResponse> create(@RequestBody RegisterPatientCommand cmd) {
        return ResponseEntity.ok(toResponse(register.execute(cmd)));
    }

    @PutMapping("/{id}")
    public ResponseEntity<PatientResponse> updateOne(
            @PathVariable UUID id,
            @RequestBody UpdatePatientBody body) {
        return ResponseEntity.ok(toResponse(update.execute(new UpdatePatientCommand(id, body.firstName(), body.lastName(), body.birthDate()))));
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteOne(@PathVariable UUID id) {
        deactivate.execute(new DeactivatePatientCommand(id));
        return ResponseEntity.noContent().build();
    }

    private PatientResponse toResponse(Patient e) {
        return new PatientResponse(
                e.getId().value(),
                e.getFirstName(),
                e.getLastName(),
                e.getBirthDate() != null ? e.getBirthDate().toString() : null
        );
    }
}
