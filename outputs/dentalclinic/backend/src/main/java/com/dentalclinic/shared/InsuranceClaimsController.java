package com.dentalclinic.shared;

import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDate;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.stream.Collectors;

@RestController
@RequestMapping("/api/insurance-claims")
@PreAuthorize("hasAnyRole('ADMIN','RECEPTIONIST')")
public class InsuranceClaimsController {

    record InsuranceClaim(String id, String patientId, String patientName, String insurer,
                          String policyNumber, String procedure, double amount, double coveredAmount,
                          String status, String submittedDate, String resolvedDate, String notes) {}

    private final Map<String, InsuranceClaim> claims = new ConcurrentHashMap<>();

    public InsuranceClaimsController() {
        Object[][] seed = {
            {"cl1","p1","García López, Ana","MAPFRE","MAP-001234","Endodoncia",850.0,680.0,"PAID","2026-02-10","2026-02-28","Aprobada 80%"},
            {"cl2","p2","Fernández Ruiz, Pedro","AXA","AXA-005678","Implante dental",1200.0,600.0,"PENDING","2026-03-01",null,"Pendiente revisión"},
            {"cl3","p3","Sánchez Torres, Luis","SANITAS","SAN-009012","Corona dental",750.0,562.5,"APPROVED","2026-02-20","2026-03-05","Aprobada 75%"},
            {"cl4","p4","Morales Vega, Carmen","DKV","DKV-003456","Ortodoncia",2400.0,0.0,"REJECTED","2026-01-15","2026-02-01","No cubierta por póliza"},
            {"cl5","p5","Jiménez Castro, Rosa","ASISA","ASI-007890","Extracción",180.0,144.0,"PAID","2026-03-10","2026-03-15","Aprobada 80%"},
            {"cl6","p6","Rodríguez Pérez, Juan","ADESLAS","ADE-001122","Limpieza dental",90.0,45.0,"PENDING","2026-03-18",null,"En tramitación"},
        };
        for (Object[] row : seed) {
            String id = (String) row[0];
            claims.put(id, new InsuranceClaim(id, (String)row[1], (String)row[2], (String)row[3],
                    (String)row[4], (String)row[5], (double)row[6], (double)row[7], (String)row[8],
                    (String)row[9], (String)row[10], (String)row[11]));
        }
    }

    @GetMapping
    public List<InsuranceClaim> listAll(@RequestParam(required = false) String status) {
        return claims.values().stream()
                .filter(c -> status == null || c.status().equals(status))
                .sorted(Comparator.comparing(InsuranceClaim::submittedDate).reversed())
                .collect(Collectors.toList());
    }

    @GetMapping("/patient/{patientId}")
    public List<InsuranceClaim> byPatient(@PathVariable String patientId) {
        return claims.values().stream()
                .filter(c -> c.patientId().equals(patientId))
                .sorted(Comparator.comparing(InsuranceClaim::submittedDate).reversed())
                .collect(Collectors.toList());
    }

    @PostMapping
    public InsuranceClaim create(@RequestBody InsuranceClaim req) {
        String id = "cl" + UUID.randomUUID().toString().substring(0, 8);
        InsuranceClaim c = new InsuranceClaim(id, req.patientId(), req.patientName(), req.insurer(),
                req.policyNumber(), req.procedure(), req.amount(), req.coveredAmount(),
                "PENDING", LocalDate.now().toString(), null, req.notes());
        claims.put(id, c);
        return c;
    }

    @PutMapping("/{id}/status")
    public ResponseEntity<InsuranceClaim> updateStatus(@PathVariable String id, @RequestBody Map<String, String> body) {
        InsuranceClaim existing = claims.get(id);
        if (existing == null) return ResponseEntity.notFound().build();
        String newStatus = body.getOrDefault("status", existing.status());
        String resolvedDate = "PAID".equals(newStatus) || "REJECTED".equals(newStatus) || "APPROVED".equals(newStatus)
                ? LocalDate.now().toString() : existing.resolvedDate();
        InsuranceClaim updated = new InsuranceClaim(id, existing.patientId(), existing.patientName(),
                existing.insurer(), existing.policyNumber(), existing.procedure(),
                existing.amount(), existing.coveredAmount(), newStatus,
                existing.submittedDate(), resolvedDate, body.getOrDefault("notes", existing.notes()));
        claims.put(id, updated);
        return ResponseEntity.ok(updated);
    }

    @GetMapping("/stats")
    public Map<String, Object> stats() {
        List<InsuranceClaim> all = new ArrayList<>(claims.values());
        Map<String, Object> result = new LinkedHashMap<>();
        result.put("total", all.size());
        result.put("pending", all.stream().filter(c -> "PENDING".equals(c.status())).count());
        result.put("approved", all.stream().filter(c -> "APPROVED".equals(c.status())).count());
        result.put("paid", all.stream().filter(c -> "PAID".equals(c.status())).count());
        result.put("rejected", all.stream().filter(c -> "REJECTED".equals(c.status())).count());
        result.put("totalAmount", all.stream().mapToDouble(InsuranceClaim::amount).sum());
        result.put("coveredAmount", all.stream().mapToDouble(InsuranceClaim::coveredAmount).sum());
        return result;
    }
}
