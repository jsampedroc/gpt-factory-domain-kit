package com.dentalclinic.shared;

import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;
import java.util.stream.Collectors;

/**
 * Electronic prescriptions management.
 * Requires ADMIN or DENTIST role.
 * Uses in-memory stub storage — wire real repositories in production.
 */
@RestController
@RequestMapping("/api/prescriptions")
@Tag(name = "Prescriptions", description = "Electronic prescriptions management")
@PreAuthorize("hasAnyRole('ADMIN','DENTIST')")
public class PrescriptionController {

    private final Map<UUID, PrescriptionResponse> store = new ConcurrentHashMap<>();

    // ---------------------------------------------------------------
    // GET /api/prescriptions/patient/{patientId}
    // ---------------------------------------------------------------

    @GetMapping("/patient/{patientId}")
    @Operation(summary = "Listar recetas de un paciente")
    public ResponseEntity<List<PrescriptionResponse>> getByPatient(
            @PathVariable UUID patientId) {

        List<PrescriptionResponse> result = store.values().stream()
                .filter(p -> patientId.equals(p.patientId()))
                .collect(Collectors.toList());

        // Seed stub data when store is empty for demo purposes
        if (result.isEmpty()) {
            PrescriptionResponse stub = new PrescriptionResponse(
                    UUID.randomUUID(),
                    patientId,
                    "Paciente Demo",
                    UUID.randomUUID(),
                    "Dr. García",
                    LocalDate.now().minusDays(3),
                    "Infección periodontal leve",
                    List.of(
                            new PrescriptionLine(
                                    "Amoxicilina 500mg",
                                    "500mg",
                                    "Cada 8 horas",
                                    7,
                                    "Tomar con alimentos"
                            ),
                            new PrescriptionLine(
                                    "Ibuprofeno 400mg",
                                    "400mg",
                                    "Cada 6 horas si hay dolor",
                                    5,
                                    "No superar 1200mg/día"
                            )
                    ),
                    "Revisión en 7 días",
                    "ACTIVA",
                    LocalDateTime.now().minusDays(3).format(DateTimeFormatter.ISO_LOCAL_DATE_TIME)
            );
            store.put(stub.id(), stub);
            result = List.of(stub);
        }

        return ResponseEntity.ok(result);
    }

    // ---------------------------------------------------------------
    // POST /api/prescriptions
    // ---------------------------------------------------------------

    @PostMapping
    @Operation(summary = "Crear nueva receta electrónica")
    public ResponseEntity<PrescriptionResponse> create(
            @Valid @RequestBody PrescriptionRequest request) {

        UUID id = UUID.randomUUID();
        PrescriptionResponse response = new PrescriptionResponse(
                id,
                request.patientId(),
                "Paciente " + request.patientId().toString().substring(0, 8),
                request.dentistId(),
                "Dr. Usuario",
                request.date() != null ? request.date() : LocalDate.now(),
                request.diagnosis(),
                request.lines() != null ? request.lines() : List.of(),
                request.notes(),
                "ACTIVA",
                LocalDateTime.now().format(DateTimeFormatter.ISO_LOCAL_DATE_TIME)
        );
        store.put(id, response);
        return ResponseEntity.ok(response);
    }

    // ---------------------------------------------------------------
    // GET /api/prescriptions/{id}
    // ---------------------------------------------------------------

    @GetMapping("/{id}")
    @Operation(summary = "Obtener receta por ID")
    public ResponseEntity<PrescriptionResponse> getById(@PathVariable UUID id) {
        PrescriptionResponse p = store.get(id);
        if (p == null) {
            return ResponseEntity.notFound().build();
        }
        return ResponseEntity.ok(p);
    }

    // ---------------------------------------------------------------
    // DELETE /api/prescriptions/{id}  — void / cancel
    // ---------------------------------------------------------------

    @DeleteMapping("/{id}")
    @Operation(summary = "Anular receta electrónica")
    public ResponseEntity<PrescriptionResponse> voidPrescription(@PathVariable UUID id) {
        PrescriptionResponse existing = store.get(id);
        if (existing == null) {
            return ResponseEntity.notFound().build();
        }
        PrescriptionResponse voided = new PrescriptionResponse(
                existing.id(),
                existing.patientId(),
                existing.patientName(),
                existing.dentistId(),
                existing.dentistName(),
                existing.date(),
                existing.diagnosis(),
                existing.lines(),
                existing.notes(),
                "ANULADA",
                existing.createdAt()
        );
        store.put(id, voided);
        return ResponseEntity.ok(voided);
    }

    // ---------------------------------------------------------------
    // Inner record types
    // ---------------------------------------------------------------

    public record PrescriptionRequest(
            UUID patientId,
            UUID dentistId,
            LocalDate date,
            String diagnosis,
            List<PrescriptionLine> lines,
            String notes
    ) {}

    public record PrescriptionLine(
            String medication,
            String dosage,
            String frequency,
            int durationDays,
            String instructions
    ) {}

    public record PrescriptionResponse(
            UUID id,
            UUID patientId,
            String patientName,
            UUID dentistId,
            String dentistName,
            LocalDate date,
            String diagnosis,
            List<PrescriptionLine> lines,
            String notes,
            String status,
            String createdAt
    ) {}
}
