package com.dentalclinic.shared;

import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.stream.Collectors;

@RestController
@RequestMapping("/api/sterilization")
@PreAuthorize("hasAnyRole('ADMIN','DENTIST','ASSISTANT')")
public class SterilizationController {

    record Instrument(String id, String name, String type, String status,
                      String location, int totalUses, int maxUses, String lastSterilizedAt) {}
    record SterilizationCycle(String id, String cycleNumber, String method,
                               String temperature, String duration, String operator,
                               String startedAt, String completedAt, String status,
                               List<String> instrumentIds) {}
    record SterilizationStats(int totalInstruments, int pendingSterilization,
                               int inProgress, int ready, int outOfService,
                               int cyclesThisMonth) {}

    private final Map<String, Instrument> instruments = new ConcurrentHashMap<>();
    private final Map<String, SterilizationCycle> cycles = new ConcurrentHashMap<>();

    public SterilizationController() {
        Object[][] instSeed = {
            {"i1","Sonda exploradora #1","SONDA","READY","Cajón A1",45,200,"2026-03-19T14:00"},
            {"i2","Sonda exploradora #2","SONDA","PENDING","Cajón A1",48,200,"2026-03-18T10:00"},
            {"i3","Espejo dental #1","ESPEJO","READY","Cajón A2",120,500,"2026-03-19T14:00"},
            {"i4","Espejo dental #2","ESPEJO","IN_USE","Sillón 2",88,500,"2026-03-18T10:00"},
            {"i5","Fórceps extracción superior","FORCEPS","PENDING","Cajón B1",30,150,"2026-03-17T09:00"},
            {"i6","Fórceps extracción inferior","FORCEPS","READY","Cajón B1",22,150,"2026-03-19T14:00"},
            {"i7","Elevador Potts","ELEVADOR","READY","Cajón B2",15,100,"2026-03-19T14:00"},
            {"i8","Lima endodoncia K25","LIMA","OUT_OF_SERVICE","Baja",100,100,"2026-03-10T08:00"},
            {"i9","Tijeras quirúrgicas","TIJERAS","READY","Cajón C1",8,80,"2026-03-19T14:00"},
            {"i10","Porta agujas","PORTA_AGUJAS","PENDING","Cajón C2",55,200,"2026-03-18T08:00"},
        };
        for (Object[] row : instSeed) {
            String id = (String) row[0];
            instruments.put(id, new Instrument(id,(String)row[1],(String)row[2],(String)row[3],
                    (String)row[4],(int)row[5],(int)row[6],(String)row[7]));
        }

        String today = LocalDate.now().toString();
        String yesterday = LocalDate.now().minusDays(1).toString();
        cycles.put("c1", new SterilizationCycle("c1","CIC-2026-031","AUTOCLAVE_134","134°C","18 min",
                "María Torres", yesterday+"T09:00", yesterday+"T09:25","COMPLETED",
                List.of("i1","i3","i6","i7","i9")));
        cycles.put("c2", new SterilizationCycle("c2","CIC-2026-032","AUTOCLAVE_134","134°C","18 min",
                "María Torres", today+"T08:30", today+"T08:55","COMPLETED",
                List.of("i1","i3","i6","i7","i9")));
        cycles.put("c3", new SterilizationCycle("c3","CIC-2026-033","AUTOCLAVE_121","121°C","30 min",
                "María Torres", today+"T14:00", null,"IN_PROGRESS",
                List.of("i2","i5","i10")));
    }

    @GetMapping("/instruments")
    public List<Instrument> listInstruments(@RequestParam(required = false) String status) {
        return instruments.values().stream()
                .filter(i -> status == null || i.status().equals(status))
                .sorted(Comparator.comparing(Instrument::name))
                .collect(Collectors.toList());
    }

    @PutMapping("/instruments/{id}/status")
    public ResponseEntity<Instrument> updateInstrumentStatus(
            @PathVariable String id, @RequestBody Map<String, String> body) {
        Instrument existing = instruments.get(id);
        if (existing == null) return ResponseEntity.notFound().build();
        Instrument updated = new Instrument(id, existing.name(), existing.type(),
                body.getOrDefault("status", existing.status()), existing.location(),
                existing.totalUses(), existing.maxUses(),
                "READY".equals(body.get("status")) ? LocalDateTime.now().toString().substring(0, 16) : existing.lastSterilizedAt());
        instruments.put(id, updated);
        return ResponseEntity.ok(updated);
    }

    @GetMapping("/cycles")
    public List<SterilizationCycle> listCycles() {
        return cycles.values().stream()
                .sorted(Comparator.comparing(SterilizationCycle::startedAt).reversed())
                .collect(Collectors.toList());
    }

    @PostMapping("/cycles")
    public SterilizationCycle createCycle(@RequestBody SterilizationCycle req) {
        String id = "c" + UUID.randomUUID().toString().substring(0, 8);
        int num = cycles.size() + 1;
        SterilizationCycle cycle = new SterilizationCycle(id,
                String.format("CIC-%s-%03d", LocalDate.now().getYear(), num),
                req.method(), req.temperature(), req.duration(), req.operator(),
                LocalDateTime.now().toString().substring(0, 16), null, "IN_PROGRESS",
                req.instrumentIds());
        cycles.put(id, cycle);
        req.instrumentIds().forEach(iid -> {
            Instrument inst = instruments.get(iid);
            if (inst != null) {
                instruments.put(iid, new Instrument(iid, inst.name(), inst.type(), "IN_STERILIZATION",
                        inst.location(), inst.totalUses(), inst.maxUses(), inst.lastSterilizedAt()));
            }
        });
        return cycle;
    }

    @PutMapping("/cycles/{id}/complete")
    public ResponseEntity<SterilizationCycle> completeCycle(@PathVariable String id) {
        SterilizationCycle existing = cycles.get(id);
        if (existing == null) return ResponseEntity.notFound().build();
        String completedAt = LocalDateTime.now().toString().substring(0, 16);
        SterilizationCycle updated = new SterilizationCycle(id, existing.cycleNumber(), existing.method(),
                existing.temperature(), existing.duration(), existing.operator(),
                existing.startedAt(), completedAt, "COMPLETED", existing.instrumentIds());
        cycles.put(id, updated);
        existing.instrumentIds().forEach(iid -> {
            Instrument inst = instruments.get(iid);
            if (inst != null) {
                instruments.put(iid, new Instrument(iid, inst.name(), inst.type(), "READY",
                        inst.location(), inst.totalUses() + 1, inst.maxUses(), completedAt));
            }
        });
        return ResponseEntity.ok(updated);
    }

    @GetMapping("/stats")
    public SterilizationStats stats() {
        List<Instrument> all = new ArrayList<>(instruments.values());
        String thisMonth = LocalDate.now().toString().substring(0, 7);
        long cyclesMonth = cycles.values().stream()
                .filter(c -> c.startedAt().startsWith(thisMonth)).count();
        return new SterilizationStats(
                all.size(),
                (int) all.stream().filter(i -> "PENDING".equals(i.status())).count(),
                (int) all.stream().filter(i -> "IN_STERILIZATION".equals(i.status())).count(),
                (int) all.stream().filter(i -> "READY".equals(i.status())).count(),
                (int) all.stream().filter(i -> "OUT_OF_SERVICE".equals(i.status())).count(),
                (int) cyclesMonth
        );
    }
}
