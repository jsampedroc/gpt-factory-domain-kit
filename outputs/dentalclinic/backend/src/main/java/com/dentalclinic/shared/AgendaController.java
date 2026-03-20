package com.dentalclinic.shared;

import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;
import io.swagger.v3.oas.annotations.tags.Tag;

import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.stream.Collectors;

@RestController
@RequestMapping("/api/agenda")
@Tag(name = "Agenda", description = "Advanced agenda: dentist view and schedule blocks")
@PreAuthorize("hasAnyRole('ADMIN','DENTIST')")
public class AgendaController {

    // ---- In-memory stores ----
    private final Map<UUID, DentistCalendarView> dentistStore = new ConcurrentHashMap<>();
    private final List<CalendarAppointment> appointmentStore = new ArrayList<>();
    private final Map<UUID, ScheduleBlock> blockStore = new ConcurrentHashMap<>();

    public AgendaController() {
        // Pre-populate 4 dentists
        DentistCalendarView d1 = new DentistCalendarView(UUID.fromString("00000000-0000-0000-0000-000000000001"), "Dra. García",     "#1976d2", "Ortodoncia",       true);
        DentistCalendarView d2 = new DentistCalendarView(UUID.fromString("00000000-0000-0000-0000-000000000002"), "Dr. Martínez",    "#e53935", "Endodoncia",       true);
        DentistCalendarView d3 = new DentistCalendarView(UUID.fromString("00000000-0000-0000-0000-000000000003"), "Dra. López",      "#43a047", "Periodoncia",      true);
        DentistCalendarView d4 = new DentistCalendarView(UUID.fromString("00000000-0000-0000-0000-000000000004"), "Dr. Fernández",   "#8e24aa", "Implantología",    true);
        dentistStore.put(d1.id(), d1);
        dentistStore.put(d2.id(), d2);
        dentistStore.put(d3.id(), d3);
        dentistStore.put(d4.id(), d4);

        // Pre-populate 10 stub appointments across 2 dentists
        String today = java.time.LocalDate.now().toString();
        appointmentStore.add(new CalendarAppointment(UUID.randomUUID(), d1.id(), d1.name(), d1.color(), UUID.randomUUID(), "Ana Pérez",     today, "09:00", "09:45", "Revisión",           "CONFIRMED",  "Box 1"));
        appointmentStore.add(new CalendarAppointment(UUID.randomUUID(), d1.id(), d1.name(), d1.color(), UUID.randomUUID(), "Luis Gómez",    today, "10:00", "10:30", "Limpieza",            "CONFIRMED",  "Box 1"));
        appointmentStore.add(new CalendarAppointment(UUID.randomUUID(), d1.id(), d1.name(), d1.color(), UUID.randomUUID(), "María Ruiz",    today, "11:00", "12:00", "Ortodoncia control",  "PENDING",    "Box 1"));
        appointmentStore.add(new CalendarAppointment(UUID.randomUUID(), d1.id(), d1.name(), d1.color(), UUID.randomUUID(), "Carlos Díaz",   today, "12:00", "13:00", "Extracción",          "CONFIRMED",  "Box 1"));
        appointmentStore.add(new CalendarAppointment(UUID.randomUUID(), d1.id(), d1.name(), d1.color(), UUID.randomUUID(), "Elena Sanz",    today, "16:00", "17:00", "Empaste",             "CANCELLED",  "Box 1"));
        appointmentStore.add(new CalendarAppointment(UUID.randomUUID(), d2.id(), d2.name(), d2.color(), UUID.randomUUID(), "Pedro Mora",    today, "09:30", "10:30", "Endodoncia",          "CONFIRMED",  "Box 2"));
        appointmentStore.add(new CalendarAppointment(UUID.randomUUID(), d2.id(), d2.name(), d2.color(), UUID.randomUUID(), "Sofía Castro",  today, "10:30", "11:00", "Revisión",            "CONFIRMED",  "Box 2"));
        appointmentStore.add(new CalendarAppointment(UUID.randomUUID(), d2.id(), d2.name(), d2.color(), UUID.randomUUID(), "Javier Ramos",  today, "11:30", "12:30", "Corona provisional",  "PENDING",    "Box 2"));
        appointmentStore.add(new CalendarAppointment(UUID.randomUUID(), d2.id(), d2.name(), d2.color(), UUID.randomUUID(), "Laura Vega",    today, "14:00", "15:00", "Blanqueamiento",      "CONFIRMED",  "Box 2"));
        appointmentStore.add(new CalendarAppointment(UUID.randomUUID(), d2.id(), d2.name(), d2.color(), UUID.randomUUID(), "Miguel Torres", today, "15:30", "16:30", "Implante fase 1",     "CONFIRMED",  "Box 2"));

        // Pre-populate 3 demo blocks
        String tomorrow = java.time.LocalDate.now().plusDays(1).toString();
        String nextWeek = java.time.LocalDate.now().plusDays(7).toString();
        blockStore.put(UUID.fromString("10000000-0000-0000-0000-000000000001"),
            new ScheduleBlock(UUID.fromString("10000000-0000-0000-0000-000000000001"), d3.id(), d3.name(), tomorrow, tomorrow, "14:00", "18:00", "Formación implantes", "TRAINING"));
        blockStore.put(UUID.fromString("10000000-0000-0000-0000-000000000002"),
            new ScheduleBlock(UUID.fromString("10000000-0000-0000-0000-000000000002"), d4.id(), d4.name(), nextWeek, java.time.LocalDate.now().plusDays(14).toString(), "09:00", "19:00", "Vacaciones verano", "VACATION"));
        blockStore.put(UUID.fromString("10000000-0000-0000-0000-000000000003"),
            new ScheduleBlock(UUID.fromString("10000000-0000-0000-0000-000000000003"), d1.id(), d1.name(), today, today, "13:00", "14:00", "Mantenimiento Box 1", "MAINTENANCE"));
    }

    // GET /api/agenda/dentists
    @GetMapping("/dentists")
    public ResponseEntity<List<DentistCalendarView>> getDentists() {
        return ResponseEntity.ok(new ArrayList<>(dentistStore.values()));
    }

    // GET /api/agenda/appointments?dentistId=&date=YYYY-MM-DD
    @GetMapping("/appointments")
    public ResponseEntity<List<CalendarAppointment>> getAppointments(
            @RequestParam(required = false) UUID dentistId,
            @RequestParam(required = false) String date) {
        List<CalendarAppointment> result = appointmentStore.stream()
            .filter(a -> dentistId == null || a.dentistId().equals(dentistId))
            .filter(a -> date == null || a.date().equals(date))
            .collect(Collectors.toList());
        return ResponseEntity.ok(result);
    }

    // GET /api/agenda/blocks
    @GetMapping("/blocks")
    public ResponseEntity<List<ScheduleBlock>> getBlocks() {
        return ResponseEntity.ok(new ArrayList<>(blockStore.values()));
    }

    // POST /api/agenda/blocks
    @PostMapping("/blocks")
    public ResponseEntity<ScheduleBlock> createBlock(@RequestBody BlockRequest req) {
        String dentistName = dentistStore.containsKey(req.dentistId())
            ? dentistStore.get(req.dentistId()).name() : "Desconocido";
        UUID id = UUID.randomUUID();
        ScheduleBlock block = new ScheduleBlock(id, req.dentistId(), dentistName,
            req.startDate(), req.endDate(), req.startTime(), req.endTime(), req.reason(), req.type());
        blockStore.put(id, block);
        return ResponseEntity.ok(block);
    }

    // DELETE /api/agenda/blocks/{id}
    @DeleteMapping("/blocks/{id}")
    public ResponseEntity<Void> deleteBlock(@PathVariable UUID id) {
        blockStore.remove(id);
        return ResponseEntity.noContent().build();
    }

    // ---- Records ----
    public record DentistCalendarView(UUID id, String name, String color, String specialty, boolean active) {}

    public record CalendarAppointment(
        UUID id, UUID dentistId, String dentistName, String dentistColor,
        UUID patientId, String patientName, String date, String startTime, String endTime,
        String procedure, String status, String operatory
    ) {}

    public record ScheduleBlock(
        UUID id, UUID dentistId, String dentistName,
        String startDate, String endDate, String startTime, String endTime,
        String reason, String type
    ) {}

    public record BlockRequest(
        UUID dentistId, String startDate, String endDate,
        String startTime, String endTime, String reason, String type
    ) {}
}
