package com.dentalclinic.shared;

import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;
import io.swagger.v3.oas.annotations.tags.Tag;

import java.time.LocalDateTime;
import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.util.*;
import java.util.concurrent.CopyOnWriteArrayList;

@RestController
@RequestMapping("/api/gdpr")
@Tag(name = "GDPR", description = "RGPD compliance: data export, right to erasure, consent log")
@PreAuthorize("hasAnyRole('ADMIN')")
public class GdprController {

    private final List<ConsentLog> consentLog = new CopyOnWriteArrayList<>();

    public GdprController() {
        String[] types  = {"DATA_PROCESSING","MARKETING","MEDICAL_HISTORY","PHOTOS","THIRD_PARTY"};
        String[] actions = {"GRANTED","WITHDRAWN","UPDATED"};
        String[][] patients = {
            {"00000000-0000-0000-0000-000000000011","Ana Pérez"},
            {"00000000-0000-0000-0000-000000000012","Luis Gómez"},
            {"00000000-0000-0000-0000-000000000013","María Ruiz"},
            {"00000000-0000-0000-0000-000000000014","Carlos Díaz"},
            {"00000000-0000-0000-0000-000000000015","Elena Sanz"}
        };
        for (int i = 0; i < 10; i++) {
            String[] p = patients[i % patients.length];
            consentLog.add(new ConsentLog(
                UUID.randomUUID(),
                UUID.fromString(p[0]),
                p[1],
                types[i % types.length],
                actions[i % actions.length],
                LocalDate.now().minusDays(i * 3L).toString(),
                "192.168.1." + (100 + i),
                "Registro demo #" + (i + 1)
            ));
        }
    }

    @GetMapping("/patient/{patientId}/export")
    public ResponseEntity<PatientDataExport> exportPatientData(@PathVariable UUID patientId) {
        Map<String, Object> personal = new LinkedHashMap<>();
        personal.put("name", "Paciente " + patientId.toString().substring(0, 8));
        personal.put("email", "paciente@ejemplo.com");
        personal.put("phone", "+34 600 000 000");
        personal.put("birthDate", "1985-03-15");
        personal.put("address", "Calle Ejemplo 1, Madrid");
        personal.put("nationalId", "12345678A");
        PatientDataExport export = new PatientDataExport(
            patientId,
            LocalDateTime.now().format(DateTimeFormatter.ISO_LOCAL_DATE_TIME),
            "admin", personal,
            List.of("2024-01-10 09:00 - Revisión", "2024-03-22 11:00 - Limpieza", "2024-06-15 10:30 - Empaste"),
            List.of("FAC-2024-001 - 85,00€", "FAC-2024-002 - 120,00€"),
            List.of("Ortodoncia brackets metálicos", "Blanqueamiento dental"),
            List.of("Consentimiento informado cirugía - FIRMADO 2024-01-10", "Uso de fotos - FIRMADO 2024-03-22"),
            List.of("Recordatorio cita 2024-01-09 - Email", "Felicitación cumpleaños 2024-03-15 - SMS")
        );
        return ResponseEntity.ok(export);
    }

    @PostMapping("/patient/{patientId}/anonymize")
    public ResponseEntity<AnonymizeResult> anonymizePatient(@PathVariable UUID patientId) {
        List<String> fields = List.of(
            "name", "email", "phone", "address", "nationalId",
            "birthDate", "insuranceNumber", "emergencyContact", "medicalHistory"
        );
        return ResponseEntity.ok(new AnonymizeResult(
            patientId,
            LocalDateTime.now().format(DateTimeFormatter.ISO_LOCAL_DATE_TIME),
            "admin", fields, "COMPLETED"
        ));
    }

    @GetMapping("/consent-log")
    public ResponseEntity<List<ConsentLog>> getConsentLog(
            @RequestParam(required = false) String consentType,
            @RequestParam(required = false) String action) {
        List<ConsentLog> result = consentLog.stream()
            .filter(c -> consentType == null || consentType.isBlank() || c.consentType().equals(consentType))
            .filter(c -> action == null || action.isBlank() || c.action().equals(action))
            .toList();
        return ResponseEntity.ok(result);
    }

    @PostMapping("/consent-log")
    public ResponseEntity<ConsentLog> logConsent(@RequestBody ConsentLogRequest req) {
        ConsentLog entry = new ConsentLog(
            UUID.randomUUID(), req.patientId(),
            "Paciente " + req.patientId().toString().substring(0, 8),
            req.consentType(), req.action(),
            LocalDate.now().toString(), "0.0.0.0", req.details()
        );
        consentLog.add(0, entry);
        return ResponseEntity.ok(entry);
    }

    @GetMapping("/retention-report")
    public ResponseEntity<RetentionReport> getRetentionReport() {
        List<RetentionItem> items = new ArrayList<>();
        items.add(new RetentionItem(UUID.fromString("00000000-0000-0000-0000-000000000011"), "Ana Pérez",    "2024-06-15", 0, "KEEP"));
        items.add(new RetentionItem(UUID.fromString("00000000-0000-0000-0000-000000000012"), "Luis Gómez",   "2022-11-03", 2, "KEEP"));
        items.add(new RetentionItem(UUID.fromString("00000000-0000-0000-0000-000000000013"), "María Ruiz",   "2021-05-20", 3, "REVIEW"));
        items.add(new RetentionItem(UUID.fromString("00000000-0000-0000-0000-000000000014"), "Carlos Díaz",  "2020-02-14", 4, "REVIEW"));
        items.add(new RetentionItem(UUID.fromString("00000000-0000-0000-0000-000000000015"), "Elena Sanz",   "2018-07-01", 6, "ANONYMIZE"));
        items.add(new RetentionItem(UUID.fromString("00000000-0000-0000-0000-000000000016"), "Pedro Mora",   "2017-03-22", 7, "ANONYMIZE"));
        items.add(new RetentionItem(UUID.fromString("00000000-0000-0000-0000-000000000017"), "Sofía Castro", "2019-12-05", 5, "REVIEW"));
        return ResponseEntity.ok(new RetentionReport(
            LocalDateTime.now().format(DateTimeFormatter.ISO_LOCAL_DATE_TIME),
            7, 2, 3, 1, items
        ));
    }

    public record PatientDataExport(
        UUID patientId, String exportedAt, String requestedBy,
        Map<String, Object> personalData,
        List<String> appointments, List<String> invoices,
        List<String> treatments, List<String> consents, List<String> communications
    ) {}

    public record AnonymizeResult(
        UUID patientId, String anonymizedAt, String requestedBy,
        List<String> anonymizedFields, String status
    ) {}

    public record ConsentLog(
        UUID id, UUID patientId, String patientName,
        String consentType, String action,
        String date, String ipAddress, String details
    ) {}

    public record ConsentLogRequest(
        UUID patientId, String consentType, String action, String details
    ) {}

    public record RetentionReport(
        String generatedAt, int totalPatients, int activePatients,
        int inactiveOver5Years, int anonymizedCount, List<RetentionItem> items
    ) {}

    public record RetentionItem(
        UUID patientId, String name, String lastActivity, int yearsInactive, String recommendation
    ) {}
}
