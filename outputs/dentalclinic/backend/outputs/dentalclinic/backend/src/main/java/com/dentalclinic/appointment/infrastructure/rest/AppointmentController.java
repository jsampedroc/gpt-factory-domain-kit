package com.dentalclinic.appointment.infrastructure.rest;

import com.dentalclinic.appointment.domain.model.Appointment;
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
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import java.util.List;
import java.util.UUID;
import java.util.stream.Collectors;

@RestController
@RequestMapping("/appointments")
@CrossOrigin(origins = "*")
public class AppointmentController {

    private final ListAllAppointmentsUseCase listAll;
    private final GetAppointmentByIdUseCase  getById;
    private final RegisterAppointmentUseCase register;
    private final UpdateAppointmentUseCase   update;
    private final DeactivateAppointmentUseCase deactivate;

    public AppointmentController(
            ListAllAppointmentsUseCase listAll,
            GetAppointmentByIdUseCase  getById,
            RegisterAppointmentUseCase register,
            UpdateAppointmentUseCase   update,
            DeactivateAppointmentUseCase deactivate) {
        this.listAll    = listAll;
        this.getById    = getById;
        this.register   = register;
        this.update     = update;
        this.deactivate = deactivate;
    }

    @GetMapping
    public List<AppointmentResponse> getAll() {
        return listAll.execute(new ListAllAppointmentsQuery())
                .stream().map(this::toResponse).collect(Collectors.toList());
    }

    @GetMapping("/{id}")
    public ResponseEntity<AppointmentResponse> getOne(@PathVariable UUID id) {
        return getById.execute(new GetAppointmentByIdQuery(id))
                .map(this::toResponse)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    @PostMapping
    public ResponseEntity<AppointmentResponse> create(@RequestBody RegisterAppointmentCommand cmd) {
        return ResponseEntity.ok(toResponse(register.execute(cmd)));
    }

    @PutMapping("/{id}")
    public ResponseEntity<AppointmentResponse> updateOne(
            @PathVariable UUID id,
            @RequestBody UpdateAppointmentBody body) {
        return ResponseEntity.ok(toResponse(update.execute(new UpdateAppointmentCommand(id, body.patientId() != null ? UUID.fromString(body.patientId()) : null, body.dentistId() != null ? UUID.fromString(body.dentistId()) : null, body.appointmentDate(), body.status()))));
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteOne(@PathVariable UUID id) {
        deactivate.execute(new DeactivateAppointmentCommand(id));
        return ResponseEntity.noContent().build();
    }

    private AppointmentResponse toResponse(Appointment e) {
        return new AppointmentResponse(
                e.getId().value(),
                e.getPatientId() != null ? e.getPatientId().toString() : null,
                e.getDentistId() != null ? e.getDentistId().toString() : null,
                e.getAppointmentDate() != null ? e.getAppointmentDate().toString() : null,
                e.getStatus() != null ? e.getStatus().getValue() : null
        );
    }
}
