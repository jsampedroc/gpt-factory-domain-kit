package com.dentalclinic.shared;

import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;

import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.stream.Collectors;

@RestController
@RequestMapping("/api/staff")
@PreAuthorize("hasRole('ADMIN')")
public class StaffController {

    record StaffMember(String id, String name, String role, String email, String phone,
                       String contractType, double hoursPerWeek, String status, String joinDate) {}
    record VacationRequest(String id, String staffId, String staffName,
                           String from, String to, String status, String notes) {}
    record ScheduleEntry(String staffId, String staffName, String dayOfWeek,
                         String startTime, String endTime) {}

    private final Map<String, StaffMember> staff = new ConcurrentHashMap<>();
    private final Map<String, VacationRequest> vacations = new ConcurrentHashMap<>();
    private final Map<String, ScheduleEntry> schedules = new ConcurrentHashMap<>();

    public StaffController() {
        Object[][] seed = {
            {"st1","Dr. Carlos Martínez","DENTIST","c.martinez@clinic.com","612345678","FULL_TIME",40.0,"ACTIVE","2020-03-01"},
            {"st2","Dra. Elena Romero","DENTIST","e.romero@clinic.com","623456789","FULL_TIME",40.0,"ACTIVE","2019-06-15"},
            {"st3","Dr. Javier Navarro","DENTIST","j.navarro@clinic.com","634567890","PART_TIME",20.0,"ACTIVE","2022-01-10"},
            {"st4","Laura Gómez","RECEPTIONIST","l.gomez@clinic.com","645678901","FULL_TIME",40.0,"ACTIVE","2021-05-20"},
            {"st5","María Torres","ASSISTANT","m.torres@clinic.com","656789012","FULL_TIME",40.0,"ACTIVE","2020-11-03"},
            {"st6","Pedro Sanz","AUXILIARY","p.sanz@clinic.com","667890123","PART_TIME",20.0,"ON_LEAVE","2023-02-28"},
        };
        for (Object[] row : seed) {
            String id = (String) row[0];
            staff.put(id, new StaffMember(id,(String)row[1],(String)row[2],(String)row[3],
                    (String)row[4],(String)row[5],(double)row[6],(String)row[7],(String)row[8]));
        }
        String[] days = {"LUNES","MARTES","MIERCOLES","JUEVES","VIERNES"};
        int i = 0;
        for (String sId : List.of("st1","st2","st4","st5")) {
            for (String day : days) {
                String eid = "sch" + (++i);
                StaffMember sm = staff.get(sId);
                schedules.put(eid, new ScheduleEntry(sId, sm.name(), day, "09:00", "17:00"));
            }
        }
        for (String day : days) {
            String eid = "sch" + (++i);
            schedules.put(eid, new ScheduleEntry("st3", "Dr. Javier Navarro", day, "09:00", "13:00"));
        }

        vacations.put("v1", new VacationRequest("v1","st1","Dr. Carlos Martínez","2026-07-14","2026-07-25","APPROVED","Vacaciones verano"));
        vacations.put("v2", new VacationRequest("v2","st2","Dra. Elena Romero","2026-08-01","2026-08-15","PENDING","Vacaciones agosto"));
        vacations.put("v3", new VacationRequest("v3","st6","Pedro Sanz","2026-03-01","2026-04-30","APPROVED","Baja médica"));
    }

    @GetMapping
    public List<StaffMember> listAll() {
        return new ArrayList<>(staff.values());
    }

    @GetMapping("/{id}")
    public ResponseEntity<StaffMember> getById(@PathVariable String id) {
        return Optional.ofNullable(staff.get(id))
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    @PostMapping
    public StaffMember create(@RequestBody StaffMember req) {
        String id = "st" + UUID.randomUUID().toString().substring(0, 8);
        StaffMember sm = new StaffMember(id, req.name(), req.role(), req.email(), req.phone(),
                req.contractType(), req.hoursPerWeek(), "ACTIVE", req.joinDate());
        staff.put(id, sm);
        return sm;
    }

    @GetMapping("/schedules")
    public List<ScheduleEntry> getSchedules(@RequestParam(required = false) String staffId) {
        return schedules.values().stream()
                .filter(s -> staffId == null || s.staffId().equals(staffId))
                .sorted(Comparator.comparing(ScheduleEntry::staffId).thenComparing(ScheduleEntry::dayOfWeek))
                .collect(Collectors.toList());
    }

    @GetMapping("/vacations")
    public List<VacationRequest> getVacations(@RequestParam(required = false) String status) {
        return vacations.values().stream()
                .filter(v -> status == null || v.status().equals(status))
                .sorted(Comparator.comparing(VacationRequest::from))
                .collect(Collectors.toList());
    }

    @PostMapping("/vacations")
    public VacationRequest createVacation(@RequestBody VacationRequest req) {
        String id = "v" + UUID.randomUUID().toString().substring(0, 8);
        VacationRequest vr = new VacationRequest(id, req.staffId(), req.staffName(),
                req.from(), req.to(), "PENDING", req.notes());
        vacations.put(id, vr);
        return vr;
    }

    @PutMapping("/vacations/{id}/approve")
    public ResponseEntity<VacationRequest> approveVacation(@PathVariable String id) {
        VacationRequest v = vacations.get(id);
        if (v == null) return ResponseEntity.notFound().build();
        VacationRequest updated = new VacationRequest(v.id(), v.staffId(), v.staffName(),
                v.from(), v.to(), "APPROVED", v.notes());
        vacations.put(id, updated);
        return ResponseEntity.ok(updated);
    }

    @GetMapping("/hours")
    public Map<String, Object> monthlyHours() {
        Map<String, Object> result = new LinkedHashMap<>();
        staff.values().forEach(sm -> {
            Map<String, Object> entry = new LinkedHashMap<>();
            entry.put("name", sm.name());
            entry.put("role", sm.role());
            entry.put("contractHours", sm.hoursPerWeek() * 4);
            entry.put("workedHours", sm.hoursPerWeek() * 4 * 0.95);
            result.put(sm.id(), entry);
        });
        return result;
    }
}
