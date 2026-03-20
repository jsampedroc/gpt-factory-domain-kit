package com.dentalclinic.shared;

import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;

/**
 * REST controller for multi-clinic location management.
 * Round 33 — in-memory implementation. Wire with real repositories in production.
 */
@RestController
@RequestMapping("/api/locations")
@Tag(name = "Locations", description = "Multi-clinic location management")
public class ClinicLocationController {

    private static final Map<UUID, ClinicLocation> STORE = new ConcurrentHashMap<>();

    static {
        UUID id1 = UUID.fromString("10000000-0000-0000-0000-000000000001");
        UUID id2 = UUID.fromString("10000000-0000-0000-0000-000000000002");
        UUID id3 = UUID.fromString("10000000-0000-0000-0000-000000000003");

        STORE.put(id1, new ClinicLocation(id1, "Clínica Central", "Calle Mayor 1", "Madrid",
                "91 100 0001", "central@dental.es", "Lun-Vie 9:00-18:00", true,
                List.of("Ortodoncia", "Implantes", "Blanqueamiento")));
        STORE.put(id2, new ClinicLocation(id2, "Clínica Norte", "Avenida Norte 45", "Barcelona",
                "93 200 0002", "norte@dental.es", "Lun-Sáb 8:00-20:00", true,
                List.of("Periodoncia", "Endodoncia", "Estética")));
        STORE.put(id3, new ClinicLocation(id3, "Clínica Sur", "Paseo del Sur 12", "Sevilla",
                "95 300 0003", "sur@dental.es", "Lun-Vie 9:00-17:00", true,
                List.of("Odontopediatría", "Cirugía oral", "Prótesis")));
    }

    /** GET /api/locations — list all clinic locations (public) */
    @GetMapping
    public ResponseEntity<List<ClinicLocation>> listAll() {
        return ResponseEntity.ok(new ArrayList<>(STORE.values()));
    }

    /** POST /api/locations — create location (ADMIN) */
    @PostMapping
    @PreAuthorize("hasAnyRole('ADMIN')")
    public ResponseEntity<ClinicLocation> create(@RequestBody LocationRequest req) {
        UUID id = UUID.randomUUID();
        ClinicLocation loc = new ClinicLocation(id, req.name(), req.address(), req.city(),
                req.phone(), req.email(), req.schedule(), true,
                req.services() != null ? req.services() : List.of());
        STORE.put(id, loc);
        return ResponseEntity.ok(loc);
    }

    /** PUT /api/locations/{id} — update location (ADMIN) */
    @PutMapping("/{id}")
    @PreAuthorize("hasAnyRole('ADMIN')")
    public ResponseEntity<ClinicLocation> update(@PathVariable UUID id, @RequestBody LocationRequest req) {
        ClinicLocation existing = STORE.get(id);
        if (existing == null) {
            return ResponseEntity.notFound().build();
        }
        ClinicLocation updated = new ClinicLocation(id, req.name(), req.address(), req.city(),
                req.phone(), req.email(), req.schedule(), existing.active(),
                req.services() != null ? req.services() : List.of());
        STORE.put(id, updated);
        return ResponseEntity.ok(updated);
    }

    /** GET /api/locations/{id}/dentists — list dentists at this location */
    @GetMapping("/{id}/dentists")
    public ResponseEntity<List<Map<String, Object>>> getDentists(@PathVariable UUID id) {
        if (!STORE.containsKey(id)) {
            return ResponseEntity.notFound().build();
        }
        List<Map<String, Object>> dentists = List.of(
                Map.of("id", UUID.randomUUID().toString(), "name", "Dr. García", "specialty", "Ortodoncista"),
                Map.of("id", UUID.randomUUID().toString(), "name", "Dra. López", "specialty", "Endodoncista")
        );
        return ResponseEntity.ok(dentists);
    }

    /** GET /api/locations/{id}/availability?date=YYYY-MM-DD — available slots at location */
    @GetMapping("/{id}/availability")
    public ResponseEntity<List<AvailableSlot>> getAvailability(
            @PathVariable UUID id,
            @RequestParam(required = false) String date) {
        if (!STORE.containsKey(id)) {
            return ResponseEntity.notFound().build();
        }
        String[] times = {"09:00","10:00","11:00","12:00","13:00","14:00","15:00","16:00"};
        boolean[] avail = {true, true, false, true, true, false, true, true};
        UUID dentistId = UUID.fromString("20000000-0000-0000-0000-000000000001");
        List<AvailableSlot> slots = new ArrayList<>();
        for (int i = 0; i < times.length; i++) {
            slots.add(new AvailableSlot(times[i], avail[i], dentistId, "Dr. García"));
        }
        return ResponseEntity.ok(slots);
    }

    // ---------------------------------------------------------------
    // Records
    // ---------------------------------------------------------------

    public record ClinicLocation(
            UUID id,
            String name,
            String address,
            String city,
            String phone,
            String email,
            String schedule,
            boolean active,
            List<String> services
    ) {}

    public record LocationRequest(
            String name,
            String address,
            String city,
            String phone,
            String email,
            String schedule,
            List<String> services
    ) {}

    public record AvailableSlot(
            String time,
            boolean available,
            UUID dentistId,
            String dentistName
    ) {}
}
