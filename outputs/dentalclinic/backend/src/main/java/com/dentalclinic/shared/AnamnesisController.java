package com.dentalclinic.shared;

import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;

/**
 * REST controller for patient anamnesis (medical history and health questionnaire).
 * Round 30 — in-memory implementation. Wire with real repositories in production.
 */
@RestController
@RequestMapping("/api/anamnesis")
@Tag(name = "Anamnesis", description = "Patient medical history and health questionnaire")
@PreAuthorize("hasAnyRole('ADMIN','DENTIST')")
public class AnamnesisController {

    // Keyed by patientId for upsert logic
    private static final Map<UUID, AnamnesisResponse> STORE = new ConcurrentHashMap<>();

    private static final DateTimeFormatter FMT = DateTimeFormatter.ISO_LOCAL_DATE_TIME;

    static {
        // Pre-populate with 3 demo anamnesis records
        UUID p1 = UUID.fromString("00000000-0000-0000-0000-000000000001");
        UUID p2 = UUID.fromString("00000000-0000-0000-0000-000000000002");
        UUID p3 = UUID.fromString("00000000-0000-0000-0000-000000000003");
        String now = LocalDateTime.now().format(FMT);

        STORE.put(p1, new AnamnesisResponse(
                UUID.randomUUID(), p1, "Paciente Demo 1",
                true, false, false, false, false, false, false, false, false, false,
                false, false, false, "",
                "Metformina 500mg",
                "Extraccion molar inferior 2020", "2023-06-15",
                false, false,
                "Maria Garcia", "+34 600 111 222",
                "Control glucemico previo a procedimientos invasivos",
                now, now));

        STORE.put(p2, new AnamnesisResponse(
                UUID.randomUUID(), p2, "Paciente Demo 2",
                false, true, true, false, false, false, false, false, true, false,
                false, true, false, "Ibuprofeno",
                "Atenolol 50mg, Acenocumarol 4mg",
                "Empastes multiples 2019", "2024-01-10",
                false, false,
                "Carlos Lopez", "+34 600 333 444",
                "Paciente anticoagulado — suspender Acenocumarol segun protocolo",
                now, now));

        STORE.put(p3, new AnamnesisResponse(
                UUID.randomUUID(), p3, "Paciente Demo 3",
                false, false, false, false, false, true, true, false, false, false,
                true, false, false, "",
                "Antirretrovirales TAR",
                "Ninguno significativo", "2024-09-20",
                true, false,
                "Ana Martinez", "+34 600 555 666",
                "Seguir protocolo de bioseguridad reforzado",
                now, now));
    }

    // ---------------------------------------------------------------
    // Endpoints
    // ---------------------------------------------------------------

    /** GET /api/anamnesis/patient/{patientId} — get anamnesis for patient (404 if none) */
    @GetMapping("/patient/{patientId}")
    public ResponseEntity<AnamnesisResponse> getByPatient(@PathVariable UUID patientId) {
        AnamnesisResponse record = STORE.get(patientId);
        if (record == null) {
            return ResponseEntity.notFound().build();
        }
        return ResponseEntity.ok(record);
    }

    /** POST /api/anamnesis — create or update anamnesis (upsert by patientId) */
    @PostMapping
    public ResponseEntity<AnamnesisResponse> upsert(@RequestBody AnamnesisRequest req) {
        String now = LocalDateTime.now().format(FMT);
        AnamnesisResponse existing = STORE.get(req.patientId());
        UUID id = existing != null ? existing.id() : UUID.randomUUID();
        String createdAt = existing != null ? existing.createdAt() : now;

        AnamnesisResponse record = new AnamnesisResponse(
                id,
                req.patientId(),
                "Paciente " + req.patientId().toString().substring(0, 8),
                req.diabetes(), req.hypertension(), req.heartDisease(), req.asthma(),
                req.epilepsy(), req.hivPositive(), req.hepatitis(), req.osteoporosis(),
                req.anticoagulants(), req.pregnant(),
                req.allergyPenicillin(), req.allergyLatex(), req.allergyAnesthesia(),
                req.otherAllergies() != null ? req.otherAllergies() : "",
                req.currentMedication() != null ? req.currentMedication() : "",
                req.previousDentalProblems() != null ? req.previousDentalProblems() : "",
                req.lastDentalVisit() != null ? req.lastDentalVisit() : "",
                req.smoker(), req.alcoholConsumer(),
                req.emergencyContact() != null ? req.emergencyContact() : "",
                req.emergencyPhone() != null ? req.emergencyPhone() : "",
                req.additionalNotes() != null ? req.additionalNotes() : "",
                createdAt,
                now
        );
        STORE.put(req.patientId(), record);
        return ResponseEntity.ok(record);
    }

    /** GET /api/anamnesis/{id} — get by ID */
    @GetMapping("/{id}")
    public ResponseEntity<AnamnesisResponse> getById(@PathVariable UUID id) {
        AnamnesisResponse record = STORE.values().stream()
                .filter(a -> a.id().equals(id))
                .findFirst()
                .orElse(null);
        if (record == null) {
            return ResponseEntity.notFound().build();
        }
        return ResponseEntity.ok(record);
    }

    // ---------------------------------------------------------------
    // Records
    // ---------------------------------------------------------------

    public record AnamnesisRequest(
            UUID patientId,
            // Medical conditions
            boolean diabetes,
            boolean hypertension,
            boolean heartDisease,
            boolean asthma,
            boolean epilepsy,
            boolean hivPositive,
            boolean hepatitis,
            boolean osteoporosis,
            boolean anticoagulants,
            boolean pregnant,
            // Allergies
            boolean allergyPenicillin,
            boolean allergyLatex,
            boolean allergyAnesthesia,
            String otherAllergies,
            // Current medication
            String currentMedication,
            // Dental history
            String previousDentalProblems,
            String lastDentalVisit,
            // Habits
            boolean smoker,
            boolean alcoholConsumer,
            // Emergency contact
            String emergencyContact,
            String emergencyPhone,
            // Notes
            String additionalNotes
    ) {}

    public record AnamnesisResponse(
            UUID id,
            UUID patientId,
            String patientName,
            // Medical conditions
            boolean diabetes,
            boolean hypertension,
            boolean heartDisease,
            boolean asthma,
            boolean epilepsy,
            boolean hivPositive,
            boolean hepatitis,
            boolean osteoporosis,
            boolean anticoagulants,
            boolean pregnant,
            // Allergies
            boolean allergyPenicillin,
            boolean allergyLatex,
            boolean allergyAnesthesia,
            String otherAllergies,
            // Current medication
            String currentMedication,
            // Dental history
            String previousDentalProblems,
            String lastDentalVisit,
            // Habits
            boolean smoker,
            boolean alcoholConsumer,
            // Emergency contact
            String emergencyContact,
            String emergencyPhone,
            // Notes
            String additionalNotes,
            String createdAt,
            String updatedAt
    ) {}
}
