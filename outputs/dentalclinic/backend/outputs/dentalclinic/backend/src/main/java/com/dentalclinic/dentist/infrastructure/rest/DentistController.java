package com.dentalclinic.dentist.infrastructure.rest;

import com.dentalclinic.dentist.domain.model.Dentist;
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
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import java.util.List;
import java.util.UUID;
import java.util.stream.Collectors;

@RestController
@RequestMapping("/dentists")
@CrossOrigin(origins = "*")
public class DentistController {

    private final ListAllDentistsUseCase listAll;
    private final GetDentistByIdUseCase  getById;
    private final RegisterDentistUseCase register;
    private final UpdateDentistUseCase   update;
    private final DeactivateDentistUseCase deactivate;

    public DentistController(
            ListAllDentistsUseCase listAll,
            GetDentistByIdUseCase  getById,
            RegisterDentistUseCase register,
            UpdateDentistUseCase   update,
            DeactivateDentistUseCase deactivate) {
        this.listAll    = listAll;
        this.getById    = getById;
        this.register   = register;
        this.update     = update;
        this.deactivate = deactivate;
    }

    @GetMapping
    public List<DentistResponse> getAll() {
        return listAll.execute(new ListAllDentistsQuery())
                .stream().map(this::toResponse).collect(Collectors.toList());
    }

    @GetMapping("/{id}")
    public ResponseEntity<DentistResponse> getOne(@PathVariable UUID id) {
        return getById.execute(new GetDentistByIdQuery(id))
                .map(this::toResponse)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    @PostMapping
    public ResponseEntity<DentistResponse> create(@RequestBody RegisterDentistCommand cmd) {
        return ResponseEntity.ok(toResponse(register.execute(cmd)));
    }

    @PutMapping("/{id}")
    public ResponseEntity<DentistResponse> updateOne(
            @PathVariable UUID id,
            @RequestBody UpdateDentistBody body) {
        return ResponseEntity.ok(toResponse(update.execute(new UpdateDentistCommand(id, body.firstName(), body.lastName(), body.licenseNumber()))));
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteOne(@PathVariable UUID id) {
        deactivate.execute(new DeactivateDentistCommand(id));
        return ResponseEntity.noContent().build();
    }

    private DentistResponse toResponse(Dentist e) {
        return new DentistResponse(
                e.getId().value(),
                e.getFirstName(),
                e.getLastName(),
                e.getLicenseNumber()
        );
    }
}
