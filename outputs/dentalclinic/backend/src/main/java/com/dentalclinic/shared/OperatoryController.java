package com.dentalclinic.shared;

import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDateTime;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.stream.Collectors;

@RestController
@RequestMapping("/api/operatories")
@PreAuthorize("hasAnyRole('ADMIN','DENTIST','RECEPTIONIST')")
public class OperatoryController {

    record Operatory(String id, String name, String type, String status, String color, String notes) {}
    record OperatorySchedule(String id, String operatoryId, String patientName, String dentistName,
                              String procedure, String startTime, String endTime, String status) {}
    record OccupancyStats(String operatoryId, String operatoryName, int totalSlots,
                          int occupiedSlots, double occupancyRate) {}

    private final Map<String, Operatory> operatories = new ConcurrentHashMap<>();
    private final Map<String, OperatorySchedule> schedules = new ConcurrentHashMap<>();

    public OperatoryController() {
        List<Operatory> seed = List.of(
            new Operatory("op1", "Sillón 1", "GENERAL", "AVAILABLE", "#4CAF50", "Uso general"),
            new Operatory("op2", "Sillón 2", "GENERAL", "OCCUPIED", "#4CAF50", "Uso general"),
            new Operatory("op3", "Sillón Ortodoncia", "ORTHODONTICS", "AVAILABLE", "#2196F3", "Equipado con scanner"),
            new Operatory("op4", "Sillón Cirugía", "SURGERY", "MAINTENANCE", "#FF9800", "Esterilización avanzada"),
            new Operatory("op5", "Sillón Radiología", "RADIOLOGY", "AVAILABLE", "#9C27B0", "RX digital")
        );
        seed.forEach(o -> operatories.put(o.id(), o));

        String today = LocalDateTime.now().toLocalDate().toString();
        List<OperatorySchedule> seedSch = List.of(
            new OperatorySchedule("s1", "op1", "García López, Ana", "Dr. Martínez", "Empaste", today + "T09:00", today + "T09:30", "CONFIRMED"),
            new OperatorySchedule("s2", "op1", "Fernández Ruiz, Pedro", "Dr. Martínez", "Limpieza", today + "T10:00", today + "T10:45", "CONFIRMED"),
            new OperatorySchedule("s3", "op2", "Sánchez Torres, Luis", "Dra. Romero", "Endodoncia", today + "T09:00", today + "T10:30", "IN_PROGRESS"),
            new OperatorySchedule("s4", "op3", "Morales Vega, Carmen", "Dr. Navarro", "Revisión ortodoncia", today + "T11:00", today + "T11:30", "CONFIRMED"),
            new OperatorySchedule("s5", "op5", "Jiménez Castro, Rosa", "Dr. Martínez", "RX panorámica", today + "T12:00", today + "T12:15", "CONFIRMED")
        );
        seedSch.forEach(s -> schedules.put(s.id(), s));
    }

    @GetMapping
    public List<Operatory> listAll() {
        return new ArrayList<>(operatories.values());
    }

    @GetMapping("/{id}")
    public ResponseEntity<Operatory> getById(@PathVariable String id) {
        return Optional.ofNullable(operatories.get(id))
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    @PostMapping
    public Operatory create(@RequestBody Operatory req) {
        String id = "op" + UUID.randomUUID().toString().substring(0, 8);
        Operatory o = new Operatory(id, req.name(), req.type(), "AVAILABLE", req.color(), req.notes());
        operatories.put(id, o);
        return o;
    }

    @PutMapping("/{id}/status")
    public ResponseEntity<Operatory> updateStatus(@PathVariable String id, @RequestBody Map<String, String> body) {
        Operatory existing = operatories.get(id);
        if (existing == null) return ResponseEntity.notFound().build();
        Operatory updated = new Operatory(id, existing.name(), existing.type(),
                body.getOrDefault("status", existing.status()), existing.color(), existing.notes());
        operatories.put(id, updated);
        return ResponseEntity.ok(updated);
    }

    @GetMapping("/schedule/today")
    public List<OperatorySchedule> todaySchedule() {
        String today = LocalDateTime.now().toLocalDate().toString();
        return schedules.values().stream()
                .filter(s -> s.startTime().startsWith(today))
                .sorted(Comparator.comparing(OperatorySchedule::startTime))
                .collect(Collectors.toList());
    }

    @GetMapping("/occupancy")
    public List<OccupancyStats> occupancyStats() {
        String today = LocalDateTime.now().toLocalDate().toString();
        return operatories.values().stream().map(op -> {
            List<OperatorySchedule> opSchedules = schedules.values().stream()
                    .filter(s -> s.operatoryId().equals(op.id()) && s.startTime().startsWith(today))
                    .collect(Collectors.toList());
            int total = 16; // 8h * 2 slots/hour
            int occupied = opSchedules.size();
            double rate = (double) occupied / total * 100;
            return new OccupancyStats(op.id(), op.name(), total, occupied, Math.round(rate * 10.0) / 10.0);
        }).collect(Collectors.toList());
    }
}
