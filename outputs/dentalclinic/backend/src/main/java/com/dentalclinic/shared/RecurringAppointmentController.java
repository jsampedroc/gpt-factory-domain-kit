package com.dentalclinic.shared;

import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.stream.Collectors;

/**
 * REST controller for recurring appointment series management.
 * Round 36 — in-memory store with auto-generated occurrences.
 */
@RestController
@RequestMapping("/api/recurring")
@Tag(name = "Recurring Appointments", description = "Recurring appointment series management")
@PreAuthorize("hasAnyRole('ADMIN','DENTIST')")
public class RecurringAppointmentController {

    private static final Map<UUID, RecurringSeries> SERIES_STORE = new ConcurrentHashMap<>();
    private static final Map<UUID, List<RecurringOccurrence>> OCCURRENCE_STORE = new ConcurrentHashMap<>();

    static {
        // Demo series 1: Orthodontics monthly
        UUID s1 = UUID.fromString("36000000-0000-0000-0000-000000000001");
        UUID p1 = UUID.fromString("11000000-0000-0000-0000-000000000001");
        UUID d1 = UUID.fromString("22000000-0000-0000-0000-000000000001");
        List<RecurringOccurrence> occ1 = generateOccurrences(s1, "2025-01-10", "2025-12-10",
                "MONTHLY", "FRIDAY", "10:00", 60);
        long done1 = occ1.stream().filter(o -> "COMPLETED".equals(o.status())).count();
        SERIES_STORE.put(s1, new RecurringSeries(s1, p1, "Ana García", d1, "Dr. García",
                "Ortodoncia", "2025-01-10", "2025-12-10", "MONTHLY", "FRIDAY", "10:00", 60,
                "Control mensual de brackets", "ACTIVE", occ1.size(), (int) done1));
        OCCURRENCE_STORE.put(s1, occ1);

        // Demo series 2: Hygiene semiannual
        UUID s2 = UUID.fromString("36000000-0000-0000-0000-000000000002");
        UUID p2 = UUID.fromString("11000000-0000-0000-0000-000000000002");
        UUID d2 = UUID.fromString("22000000-0000-0000-0000-000000000002");
        List<RecurringOccurrence> occ2 = generateOccurrences(s2, "2024-06-15", "2026-06-15",
                "SEMIANNUAL", "MONDAY", "09:00", 45);
        long done2 = occ2.stream().filter(o -> "COMPLETED".equals(o.status())).count();
        SERIES_STORE.put(s2, new RecurringSeries(s2, p2, "Carlos López", d2, "Dra. López",
                "Higiene dental", "2024-06-15", "2026-06-15", "SEMIANNUAL", "MONDAY", "09:00", 45,
                "Limpieza semestral", "ACTIVE", occ2.size(), (int) done2));
        OCCURRENCE_STORE.put(s2, occ2);

        // Demo series 3: Annual checkup
        UUID s3 = UUID.fromString("36000000-0000-0000-0000-000000000003");
        UUID p3 = UUID.fromString("11000000-0000-0000-0000-000000000003");
        UUID d3 = UUID.fromString("22000000-0000-0000-0000-000000000003");
        List<RecurringOccurrence> occ3 = generateOccurrences(s3, "2022-03-20", "2027-03-20",
                "ANNUAL", "WEDNESDAY", "11:00", 30);
        long done3 = occ3.stream().filter(o -> "COMPLETED".equals(o.status())).count();
        SERIES_STORE.put(s3, new RecurringSeries(s3, p3, "María Fernández", d3, "Dr. Martínez",
                "Revisión anual", "2022-03-20", "2027-03-20", "ANNUAL", "WEDNESDAY", "11:00", 30,
                "Chequeo anual completo", "ACTIVE", occ3.size(), (int) done3));
        OCCURRENCE_STORE.put(s3, occ3);
    }

    /** GET /api/recurring/patient/{patientId} — list recurring series for a patient */
    @GetMapping("/patient/{patientId}")
    public ResponseEntity<List<RecurringSeries>> listByPatient(@PathVariable UUID patientId) {
        List<RecurringSeries> result = SERIES_STORE.values().stream()
                .filter(s -> patientId.equals(s.patientId()))
                .collect(Collectors.toList());
        return ResponseEntity.ok(result);
    }

    /** POST /api/recurring — create a recurring series */
    @PostMapping
    public ResponseEntity<RecurringSeries> createSeries(@RequestBody RecurringSeriesRequest req) {
        UUID seriesId = UUID.randomUUID();
        List<RecurringOccurrence> occurrences = generateOccurrences(
                seriesId, req.startDate(), req.endDate(), req.frequency(),
                req.dayOfWeek(), req.time(), req.durationMinutes());
        RecurringSeries series = new RecurringSeries(
                seriesId, req.patientId(), "Paciente", req.dentistId(), "Dentista",
                req.procedure(), req.startDate(), req.endDate(), req.frequency(),
                req.dayOfWeek(), req.time(), req.durationMinutes(),
                req.notes(), "ACTIVE", occurrences.size(), 0);
        SERIES_STORE.put(seriesId, series);
        OCCURRENCE_STORE.put(seriesId, occurrences);
        return ResponseEntity.ok(series);
    }

    /** DELETE /api/recurring/{seriesId} — cancel entire series */
    @DeleteMapping("/{seriesId}")
    public ResponseEntity<Map<String, String>> cancelSeries(@PathVariable UUID seriesId) {
        RecurringSeries existing = SERIES_STORE.get(seriesId);
        if (existing == null) return ResponseEntity.notFound().build();
        RecurringSeries cancelled = new RecurringSeries(
                existing.id(), existing.patientId(), existing.patientName(),
                existing.dentistId(), existing.dentistName(), existing.procedure(),
                existing.startDate(), existing.endDate(), existing.frequency(),
                existing.dayOfWeek(), existing.time(), existing.durationMinutes(),
                existing.notes(), "CANCELLED", existing.totalOccurrences(), existing.completedOccurrences());
        SERIES_STORE.put(seriesId, cancelled);
        List<RecurringOccurrence> occs = OCCURRENCE_STORE.getOrDefault(seriesId, new ArrayList<>());
        List<RecurringOccurrence> updated = occs.stream().map(o ->
                "SCHEDULED".equals(o.status())
                        ? new RecurringOccurrence(o.id(), o.seriesId(), o.date(), o.time(), "CANCELLED", o.notes())
                        : o
        ).collect(Collectors.toList());
        OCCURRENCE_STORE.put(seriesId, updated);
        return ResponseEntity.ok(Map.of("message", "Serie cancelada", "seriesId", seriesId.toString()));
    }

    /** GET /api/recurring/{seriesId}/occurrences — list all generated occurrences */
    @GetMapping("/{seriesId}/occurrences")
    public ResponseEntity<List<RecurringOccurrence>> listOccurrences(@PathVariable UUID seriesId) {
        List<RecurringOccurrence> occs = OCCURRENCE_STORE.getOrDefault(seriesId, Collections.emptyList());
        return ResponseEntity.ok(occs);
    }

    /** POST /api/recurring/{seriesId}/skip/{occurrenceDate} — skip one occurrence */
    @PostMapping("/{seriesId}/skip/{occurrenceDate}")
    public ResponseEntity<RecurringOccurrence> skipOccurrence(
            @PathVariable UUID seriesId,
            @PathVariable String occurrenceDate) {
        List<RecurringOccurrence> occs = OCCURRENCE_STORE.getOrDefault(seriesId, new ArrayList<>());
        List<RecurringOccurrence> updated = new ArrayList<>();
        RecurringOccurrence skipped = null;
        for (RecurringOccurrence o : occs) {
            if (occurrenceDate.equals(o.date()) && "SCHEDULED".equals(o.status())) {
                skipped = new RecurringOccurrence(o.id(), o.seriesId(), o.date(), o.time(), "SKIPPED", o.notes());
                updated.add(skipped);
            } else {
                updated.add(o);
            }
        }
        OCCURRENCE_STORE.put(seriesId, updated);
        if (skipped == null) return ResponseEntity.notFound().build();
        return ResponseEntity.ok(skipped);
    }

    // ---- Helpers ----

    private static List<RecurringOccurrence> generateOccurrences(
            UUID seriesId, String startDate, String endDate,
            String frequency, String dayOfWeek, String time, int durationMinutes) {
        List<RecurringOccurrence> list = new ArrayList<>();
        LocalDate today = LocalDate.now();
        try {
            LocalDate start = LocalDate.parse(startDate);
            LocalDate end = LocalDate.parse(endDate);
            LocalDate current = start;
            while (!current.isAfter(end)) {
                String status = current.isBefore(today) ? "COMPLETED" : "SCHEDULED";
                list.add(new RecurringOccurrence(UUID.randomUUID(), seriesId,
                        current.format(DateTimeFormatter.ISO_LOCAL_DATE), time, status, ""));
                current = nextDate(current, frequency);
                if (list.size() > 500) break; // safety cap
            }
        } catch (Exception ignored) {}
        return list;
    }

    private static LocalDate nextDate(LocalDate current, String frequency) {
        return switch (frequency) {
            case "WEEKLY"     -> current.plusWeeks(1);
            case "BIWEEKLY"   -> current.plusWeeks(2);
            case "MONTHLY"    -> current.plusMonths(1);
            case "QUARTERLY"  -> current.plusMonths(3);
            case "SEMIANNUAL" -> current.plusMonths(6);
            case "ANNUAL"     -> current.plusYears(1);
            default           -> current.plusMonths(1);
        };
    }

    // ---- Records ----

    public record RecurringSeriesRequest(
        UUID patientId, UUID dentistId, String procedure,
        String startDate, String endDate, String frequency,
        String dayOfWeek, String time, int durationMinutes, String notes
    ) {}

    public record RecurringSeries(
        UUID id, UUID patientId, String patientName, UUID dentistId, String dentistName,
        String procedure, String startDate, String endDate, String frequency,
        String dayOfWeek, String time, int durationMinutes, String notes,
        String status, int totalOccurrences, int completedOccurrences
    ) {}

    public record RecurringOccurrence(
        UUID id, UUID seriesId, String date, String time, String status, String notes
    ) {}
}
