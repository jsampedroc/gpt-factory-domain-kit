package com.dentalclinic.shared;

import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;
import io.swagger.v3.oas.annotations.tags.Tag;

import java.time.LocalDateTime;
import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.stream.Collectors;

@RestController
@RequestMapping("/api/waitlist")
@Tag(name = "Waitlist", description = "Appointment waitlist for last-minute slots")
@PreAuthorize("hasAnyRole('ADMIN','DENTIST')")
public class WaitlistController {

    private final Map<UUID, WaitlistEntry> store = new ConcurrentHashMap<>();

    public WaitlistController() {
        Object[][] demo = {
            { UUID.fromString("00000000-0000-0000-0000-000000000011"), "Ana Pérez",    "+34 600 111 111",
              UUID.fromString("00000000-0000-0000-0000-000000000001"), "Dra. García",
              "Revisión ortodoncia", "L,M,X", "MORNING",   "HIGH",   "WAITING",   null },
            { UUID.fromString("00000000-0000-0000-0000-000000000012"), "Luis Gómez",   "+34 600 222 222",
              UUID.fromString("00000000-0000-0000-0000-000000000002"), "Dr. Martínez",
              "Endodoncia urgente",  "X,J,V", "ANY",       "HIGH",   "WAITING",   null },
            { UUID.fromString("00000000-0000-0000-0000-000000000013"), "María Ruiz",   "+34 600 333 333",
              UUID.fromString("00000000-0000-0000-0000-000000000003"), "Dra. López",
              "Limpieza",            "L,V",   "AFTERNOON", "NORMAL", "NOTIFIED",
              LocalDateTime.now().minusHours(2).format(DateTimeFormatter.ISO_LOCAL_DATE_TIME) },
            { UUID.fromString("00000000-0000-0000-0000-000000000014"), "Carlos Díaz",  "+34 600 444 444",
              UUID.fromString("00000000-0000-0000-0000-000000000001"), "Dra. García",
              "Empaste",             "M,J",   "MORNING",   "NORMAL", "WAITING",   null },
            { UUID.fromString("00000000-0000-0000-0000-000000000015"), "Elena Sanz",   "+34 600 555 555",
              UUID.fromString("00000000-0000-0000-0000-000000000004"), "Dr. Fernández",
              "Implante revisión",   "L,M,X,J,V", "ANY",  "LOW",    "WAITING",   null },
            { UUID.fromString("00000000-0000-0000-0000-000000000016"), "Pedro Mora",   "+34 600 666 666",
              UUID.fromString("00000000-0000-0000-0000-000000000002"), "Dr. Martínez",
              "Corona provisional",  "J,V,S", "AFTERNOON", "LOW",    "WAITING",   null },
        };
        for (int i = 0; i < demo.length; i++) {
            UUID id = UUID.randomUUID();
            String addedAt = LocalDateTime.now().minusDays(demo.length - i)
                .format(DateTimeFormatter.ISO_LOCAL_DATE_TIME);
            store.put(id, new WaitlistEntry(
                id,
                (UUID)   demo[i][0],  (String) demo[i][1],  (String) demo[i][2],
                (UUID)   demo[i][3],  (String) demo[i][4],
                (String) demo[i][5],  (String) demo[i][6],  (String) demo[i][7],
                (String) demo[i][8],  (String) demo[i][9],  addedAt,
                (String) demo[i][10]
            ));
        }
    }

    @GetMapping
    public ResponseEntity<List<WaitlistEntry>> getWaitlist() {
        List<WaitlistEntry> sorted = store.values().stream()
            .sorted(Comparator.comparing((WaitlistEntry e) -> switch (e.priority()) {
                case "HIGH"   -> 0;
                case "NORMAL" -> 1;
                default       -> 2;
            }).thenComparing(WaitlistEntry::addedAt))
            .collect(Collectors.toList());
        return ResponseEntity.ok(sorted);
    }

    @PostMapping
    public ResponseEntity<WaitlistEntry> addToWaitlist(@RequestBody WaitlistRequest req) {
        UUID id = UUID.randomUUID();
        WaitlistEntry entry = new WaitlistEntry(
            id, req.patientId(),
            "Paciente " + req.patientId().toString().substring(0, 8),
            req.patientPhone(), req.preferredDentistId(), "Dentista asignado",
            req.procedure(), req.preferredDays(), req.preferredTime(),
            req.priority() != null ? req.priority() : "NORMAL",
            "WAITING",
            LocalDateTime.now().format(DateTimeFormatter.ISO_LOCAL_DATE_TIME),
            null
        );
        store.put(id, entry);
        return ResponseEntity.ok(entry);
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> removeFromWaitlist(@PathVariable UUID id) {
        store.remove(id);
        return ResponseEntity.noContent().build();
    }

    @PostMapping("/{id}/notify")
    public ResponseEntity<WaitlistEntry> notifyPatient(@PathVariable UUID id) {
        WaitlistEntry e = store.get(id);
        if (e == null) return ResponseEntity.notFound().build();
        WaitlistEntry updated = new WaitlistEntry(
            e.id(), e.patientId(), e.patientName(), e.patientPhone(),
            e.preferredDentistId(), e.preferredDentistName(),
            e.procedure(), e.preferredDays(), e.preferredTime(),
            e.priority(), "NOTIFIED", e.addedAt(),
            LocalDateTime.now().format(DateTimeFormatter.ISO_LOCAL_DATE_TIME)
        );
        store.put(id, updated);
        return ResponseEntity.ok(updated);
    }

    @PostMapping("/{id}/book")
    public ResponseEntity<WaitlistEntry> bookSlot(@PathVariable UUID id) {
        WaitlistEntry e = store.get(id);
        if (e == null) return ResponseEntity.notFound().build();
        WaitlistEntry updated = new WaitlistEntry(
            e.id(), e.patientId(), e.patientName(), e.patientPhone(),
            e.preferredDentistId(), e.preferredDentistName(),
            e.procedure(), e.preferredDays(), e.preferredTime(),
            e.priority(), "BOOKED", e.addedAt(), e.notifiedAt()
        );
        store.put(id, updated);
        return ResponseEntity.ok(updated);
    }

    @GetMapping("/available-slots")
    public ResponseEntity<List<AvailableSlot>> getAvailableSlots(
            @RequestParam(required = false) String date) {
        String targetDate = (date != null && !date.isBlank()) ? date : LocalDate.now().toString();
        List<AvailableSlot> slots = List.of(
            new AvailableSlot(targetDate, "09:00", UUID.fromString("00000000-0000-0000-0000-000000000001"), "Dra. García",   "Box 1"),
            new AvailableSlot(targetDate, "11:30", UUID.fromString("00000000-0000-0000-0000-000000000002"), "Dr. Martínez",  "Box 2"),
            new AvailableSlot(targetDate, "16:00", UUID.fromString("00000000-0000-0000-0000-000000000003"), "Dra. López",    "Box 3"),
            new AvailableSlot(targetDate, "17:30", UUID.fromString("00000000-0000-0000-0000-000000000004"), "Dr. Fernández", "Box 4")
        );
        return ResponseEntity.ok(slots);
    }

    public record WaitlistEntry(
        UUID id, UUID patientId, String patientName, String patientPhone,
        UUID preferredDentistId, String preferredDentistName,
        String procedure, String preferredDays, String preferredTime,
        String priority, String status, String addedAt, String notifiedAt
    ) {}

    public record WaitlistRequest(
        UUID patientId, String patientPhone, UUID preferredDentistId,
        String procedure, String preferredDays, String preferredTime,
        String priority, String notes
    ) {}

    public record AvailableSlot(
        String date, String time, UUID dentistId, String dentistName, String operatory
    ) {}
}
