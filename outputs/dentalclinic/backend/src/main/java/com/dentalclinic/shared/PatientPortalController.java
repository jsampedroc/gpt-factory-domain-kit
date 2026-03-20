package com.dentalclinic.shared;

import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.UUID;

/**
 * Public-facing patient portal endpoints.
 * No authentication required — patients access using their patient ID.
 * In production, wire with real repositories and validate patient identity.
 */
@RestController
@RequestMapping("/api/portal")
@Tag(name = "Patient Portal", description = "Public endpoints for patient self-service")
public class PatientPortalController {

    /**
     * Returns the appointment history for a given patient.
     * GET /api/portal/appointments?patientId={uuid}
     * Stub implementation — replace with real repository query.
     */
    @GetMapping("/appointments")
    @Operation(summary = "Obtener historial de citas del paciente")
    public ResponseEntity<List<AppointmentSummary>> getAppointments(
            @RequestParam UUID patientId) {

        // Stub data — replace with: appointmentRepo.findByPatientId(patientId)
        List<AppointmentSummary> result = List.of(
                new AppointmentSummary(
                        UUID.randomUUID(),
                        "2025-11-10",
                        "Dr. García",
                        "Limpieza dental",
                        "COMPLETED"
                ),
                new AppointmentSummary(
                        UUID.randomUUID(),
                        "2025-12-15",
                        "Dra. Martínez",
                        "Revisión ortodoncia",
                        "CONFIRMED"
                )
        );
        return ResponseEntity.ok(result);
    }

    /**
     * Accepts a new appointment request from a patient.
     * POST /api/portal/appointments/request
     */
    @PostMapping("/appointments/request")
    @Operation(summary = "Solicitar nueva cita (paciente)")
    public ResponseEntity<String> requestAppointment(
            @RequestBody AppointmentRequest request) {

        // Stub — in production persist to a PendingAppointmentRequest entity
        // and trigger notification to clinic staff
        return ResponseEntity.ok(
                "Solicitud recibida para el paciente " + request.patientId() +
                " el " + request.date() + ". Le contactaremos para confirmar."
        );
    }

    // ---------------------------------------------------------------
    // Inner record types
    // ---------------------------------------------------------------

    public record AppointmentSummary(
            UUID id,
            String date,
            String dentist,
            String procedure,
            String status
    ) {}

    public record AppointmentRequest(
            UUID patientId,
            String date,
            String procedure,
            String notes
    ) {}
}
