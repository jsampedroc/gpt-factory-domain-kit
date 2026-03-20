package com.dentalclinic.shared;

import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;

import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.stream.Collectors;

@RestController
@RequestMapping("/api/patient-map")
@PreAuthorize("hasAnyRole('ADMIN','DENTIST')")
public class PatientMapController {

    record PatientLocation(String patientId, String patientName, String city,
                            String postalCode, String province, double lat, double lng,
                            int appointmentsCount, String lastVisit) {}
    record MapStats(int totalPatients, Map<String, Long> byProvince,
                    Map<String, Long> byPostalCode, double centerLat, double centerLng) {}

    private final Map<String, PatientLocation> locations = new ConcurrentHashMap<>();

    public PatientMapController() {
        Object[][] seed = {
            {"p1","García López, Ana","Madrid","28001","Madrid",40.4168,-3.7038,12,"2026-03-15"},
            {"p2","Fernández Ruiz, Pedro","Madrid","28080","Madrid",40.4523,-3.6918,8,"2026-03-10"},
            {"p3","Sánchez Torres, Luis","Alcalá de Henares","28801","Madrid",40.4821,-3.3598,5,"2026-02-28"},
            {"p4","Morales Vega, Carmen","Getafe","28901","Madrid",40.3055,-3.7325,3,"2026-03-01"},
            {"p5","Jiménez Castro, Rosa","Madrid","28010","Madrid",40.4278,-3.6913,15,"2026-03-18"},
            {"p6","Rodríguez Pérez, Juan","Leganés","28911","Madrid",40.3288,-3.7638,2,"2026-01-20"},
            {"p7","López Martín, Elena","Madrid","28020","Madrid",40.4487,-3.7136,7,"2026-03-12"},
            {"p8","González Díaz, Miguel","Majadahonda","28220","Madrid",40.4736,-3.8722,4,"2026-02-15"},
            {"p9","Hernández Ruiz, Sofía","Pozuelo de Alarcón","28223","Madrid",40.4388,-3.8138,6,"2026-03-05"},
            {"p10","Martínez López, Carlos","Móstoles","28931","Madrid",40.3226,-3.8648,1,"2025-12-10"},
            {"p11","Torres Sánchez, Isabel","Alcobendas","28100","Madrid",40.5448,-3.6387,9,"2026-03-08"},
            {"p12","Flores Moreno, David","Torrejón de Ardoz","28850","Madrid",40.4608,-3.4621,3,"2026-02-20"},
            {"p13","Navarro Gil, Patricia","Valdemoro","28340","Madrid",40.1938,-3.6802,2,"2026-01-15"},
            {"p14","Ruiz Castro, Antonio","Aranjuez","28300","Madrid",40.0325,-3.6035,4,"2026-03-02"},
            {"p15","Molina Vega, Laura","Madrid","28045","Madrid",40.3987,-3.6980,11,"2026-03-17"},
        };
        for (Object[] row : seed) {
            String id = (String) row[0];
            locations.put(id, new PatientLocation(id,(String)row[1],(String)row[2],(String)row[3],
                    (String)row[4],(double)row[5],(double)row[6],(int)row[7],(String)row[8]));
        }
    }

    @GetMapping
    public List<PatientLocation> listAll(
            @RequestParam(required = false) String province,
            @RequestParam(required = false) String city) {
        return locations.values().stream()
                .filter(p -> province == null || p.province().equalsIgnoreCase(province))
                .filter(p -> city == null || p.city().equalsIgnoreCase(city))
                .sorted(Comparator.comparing(PatientLocation::patientName))
                .collect(Collectors.toList());
    }

    @GetMapping("/stats")
    public MapStats stats() {
        List<PatientLocation> all = new ArrayList<>(locations.values());
        Map<String, Long> byProv = all.stream()
                .collect(Collectors.groupingBy(PatientLocation::province, Collectors.counting()));
        Map<String, Long> byCP = all.stream()
                .collect(Collectors.groupingBy(PatientLocation::postalCode, Collectors.counting()));
        double avgLat = all.stream().mapToDouble(PatientLocation::lat).average().orElse(40.4168);
        double avgLng = all.stream().mapToDouble(PatientLocation::lng).average().orElse(-3.7038);
        return new MapStats(all.size(), byProv, byCP, avgLat, avgLng);
    }

    @GetMapping("/heatmap")
    public List<Map<String, Object>> heatmap() {
        return locations.values().stream().map(p -> {
            Map<String, Object> point = new LinkedHashMap<>();
            point.put("lat", p.lat());
            point.put("lng", p.lng());
            point.put("weight", p.appointmentsCount());
            point.put("label", p.city());
            return point;
        }).collect(Collectors.toList());
    }
}
