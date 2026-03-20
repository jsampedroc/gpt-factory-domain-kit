package com.dentalclinic.shared;

import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;
import java.util.stream.Collectors;

/**
 * REST controller for managing informed consent forms (consentimientos informados).
 * Round 27 — in-memory implementation. Wire with real repositories in production.
 */
@RestController
@RequestMapping("/api/consents")
@Tag(name = "Consents", description = "Gestion de consentimientos informados")
@PreAuthorize("hasAnyRole('ADMIN','DENTIST')")
public class ConsentController {

    private static final Map<UUID, ConsentRecord> STORE = new ConcurrentHashMap<>();

    private static final String DEFAULT_CONSENT_TEXT =
        "CONSENTIMIENTO INFORMADO PARA TRATAMIENTO DENTAL\n\n" +
        "Yo, el/la abajo firmante, autorizo al profesional odontologo a realizar los procedimientos " +
        "de implantologia, endodoncia, extracciones y demas tratamientos dentales que se consideren " +
        "necesarios para el mantenimiento de mi salud bucodental, habiendo sido informado/a de los " +
        "riesgos y beneficios asociados a dichos procedimientos.\n\n" +
        "Declaro haber recibido explicacion sobre las alternativas de tratamiento disponibles, " +
        "los posibles riesgos e inconvenientes, las consecuencias previsibles de su realizacion " +
        "y las contraindicaciones. Me ha sido facilitada la oportunidad de formular preguntas " +
        "sobre el procedimiento y estas han sido contestadas de forma satisfactoria.\n\n" +
        "Entiendo que puedo revocar este consentimiento en cualquier momento antes del inicio " +
        "del procedimiento, sin que ello afecte a la atencion medica que deba recibir posteriormente. " +
        "Este documento se rige por la Ley 41/2002 de Autonomia del Paciente.";

    // ---------------------------------------------------------------
    // Endpoints
    // ---------------------------------------------------------------

    /** GET /api/consents/patient/{patientId} — list consents for a patient */
    @GetMapping("/patient/{patientId}")
    public ResponseEntity<List<ConsentResponse>> listByPatient(@PathVariable UUID patientId) {
        List<ConsentResponse> result = STORE.values().stream()
                .filter(c -> c.patientId().equals(patientId))
                .map(ConsentController::toResponse)
                .collect(Collectors.toList());
        return ResponseEntity.ok(result);
    }

    /** POST /api/consents — create a new consent record */
    @PostMapping
    public ResponseEntity<ConsentResponse> create(@RequestBody ConsentRequest req) {
        String text = (req.consentText() != null && !req.consentText().isBlank())
                ? req.consentText()
                : DEFAULT_CONSENT_TEXT;
        ConsentRecord record = new ConsentRecord(
                UUID.randomUUID(),
                req.patientId(),
                "Paciente " + req.patientId().toString().substring(0, 8),
                req.dentistId(),
                "Dr. " + req.dentistId().toString().substring(0, 8),
                req.procedure(),
                text,
                req.date() != null ? req.date() : LocalDate.now(),
                "PENDIENTE",
                null
        );
        STORE.put(record.id(), record);
        return ResponseEntity.ok(toResponse(record));
    }

    /** GET /api/consents/{id} — get a single consent by id */
    @GetMapping("/{id}")
    public ResponseEntity<ConsentResponse> getById(@PathVariable UUID id) {
        ConsentRecord record = STORE.get(id);
        if (record == null) {
            return ResponseEntity.notFound().build();
        }
        return ResponseEntity.ok(toResponse(record));
    }

    /** POST /api/consents/{id}/sign — patient signs the consent */
    @PostMapping("/{id}/sign")
    public ResponseEntity<ConsentResponse> sign(@PathVariable UUID id) {
        ConsentRecord existing = STORE.get(id);
        if (existing == null) {
            return ResponseEntity.notFound().build();
        }
        String signedAt = LocalDateTime.now().format(DateTimeFormatter.ISO_LOCAL_DATE_TIME);
        ConsentRecord signed = new ConsentRecord(
                existing.id(),
                existing.patientId(),
                existing.patientName(),
                existing.dentistId(),
                existing.dentistName(),
                existing.procedure(),
                existing.consentText(),
                existing.date(),
                "FIRMADO",
                signedAt
        );
        STORE.put(id, signed);
        return ResponseEntity.ok(toResponse(signed));
    }

    // ---------------------------------------------------------------
    // Inner record types
    // ---------------------------------------------------------------

    public record ConsentRequest(
            UUID patientId,
            UUID dentistId,
            String procedure,
            String consentText,
            LocalDate date
    ) {}

    public record ConsentResponse(
            UUID id,
            UUID patientId,
            String patientName,
            UUID dentistId,
            String dentistName,
            String procedure,
            String consentText,
            LocalDate date,
            String status,
            String signedAt
    ) {}

    private record ConsentRecord(
            UUID id,
            UUID patientId,
            String patientName,
            UUID dentistId,
            String dentistName,
            String procedure,
            String consentText,
            LocalDate date,
            String status,
            String signedAt
    ) {}

    private static ConsentResponse toResponse(ConsentRecord r) {
        return new ConsentResponse(
                r.id(), r.patientId(), r.patientName(),
                r.dentistId(), r.dentistName(),
                r.procedure(), r.consentText(),
                r.date(), r.status(), r.signedAt()
        );
    }
}
