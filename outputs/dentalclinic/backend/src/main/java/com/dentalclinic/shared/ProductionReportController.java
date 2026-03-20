package com.dentalclinic.shared;

import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.YearMonth;
import java.util.*;

/**
 * Business intelligence and production reports for the dental practice.
 * All endpoints require ADMIN or DENTIST role.
 * In production, wire with real JPA repositories for each aggregate.
 */
@RestController
@RequestMapping("/api/reports")
@Tag(name = "Reports", description = "Practice production and BI reports")
@PreAuthorize("hasAnyRole('ADMIN', 'DENTIST')")
public class ProductionReportController {

    /**
     * Monthly production summary.
     * Replace stub with: SELECT SUM(i.amount), COUNT(i) FROM Invoice i
     *   WHERE i.createdAt BETWEEN :from AND :to GROUP BY MONTH(i.createdAt)
     */
    @GetMapping("/production/monthly")
    @Operation(summary = "Monthly production totals for the last N months")
    public ResponseEntity<List<MonthlyProduction>> monthlyProduction(
            @RequestParam(defaultValue = "12") int months) {
        List<MonthlyProduction> result = new ArrayList<>();
        YearMonth current = YearMonth.now();
        Random rnd = new Random(42); // deterministic stub data
        for (int i = months - 1; i >= 0; i--) {
            YearMonth ym = current.minusMonths(i);
            result.add(new MonthlyProduction(
                    ym.toString(),
                    BigDecimal.valueOf(8000 + rnd.nextInt(6000)),
                    BigDecimal.valueOf(6000 + rnd.nextInt(4000)),
                    20 + rnd.nextInt(30)
            ));
        }
        return ResponseEntity.ok(result);
    }

    /**
     * Production breakdown by dentist for a date range.
     */
    @GetMapping("/production/by-dentist")
    @Operation(summary = "Production totals grouped by dentist")
    public ResponseEntity<List<DentistProduction>> byDentist(
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate from,
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate to) {
        // Stub — replace with: SELECT d.name, SUM(i.amount) FROM Invoice i JOIN Dentist d ON ...
        List<DentistProduction> result = List.of(
                new DentistProduction("Dr. García", BigDecimal.valueOf(12400), 45),
                new DentistProduction("Dra. Martínez", BigDecimal.valueOf(9800), 38),
                new DentistProduction("Dr. López", BigDecimal.valueOf(7200), 29)
        );
        return ResponseEntity.ok(result);
    }

    /**
     * Top procedures by revenue and frequency.
     */
    @GetMapping("/production/top-procedures")
    @Operation(summary = "Top dental procedures by revenue")
    public ResponseEntity<List<ProcedureStats>> topProcedures(
            @RequestParam(defaultValue = "10") int limit) {
        // Stub — replace with query over TreatmentPlanItem grouped by procedureCode
        List<ProcedureStats> result = List.of(
                new ProcedureStats("IMP001", "Implante dental", 42, BigDecimal.valueOf(63000)),
                new ProcedureStats("PRO002", "Corona zirconio", 68, BigDecimal.valueOf(40800)),
                new ProcedureStats("END002", "Endodoncia multirradicular", 95, BigDecimal.valueOf(28500)),
                new ProcedureStats("PRO001", "Corona metal-porcelana", 54, BigDecimal.valueOf(21600)),
                new ProcedureStats("OBT002", "Obturación 2 caras", 187, BigDecimal.valueOf(16830)),
                new ProcedureStats("PER002", "Raspado y alisado", 76, BigDecimal.valueOf(15200)),
                new ProcedureStats("BLA001", "Blanqueamiento", 63, BigDecimal.valueOf(12600)),
                new ProcedureStats("EXT002", "Extracción quirúrgica", 89, BigDecimal.valueOf(11125)),
                new ProcedureStats("OBT003", "Obturación 3 caras", 134, BigDecimal.valueOf(10720)),
                new ProcedureStats("PER001", "Tartrectomía", 210, BigDecimal.valueOf(10500))
        ).subList(0, Math.min(limit, 10));
        return ResponseEntity.ok(result);
    }

    /**
     * Appointment cancellation / no-show analysis.
     */
    @GetMapping("/cancellations")
    @Operation(summary = "Cancellation and no-show rates by month")
    public ResponseEntity<List<CancellationStats>> cancellations(
            @RequestParam(defaultValue = "6") int months) {
        List<CancellationStats> result = new ArrayList<>();
        YearMonth current = YearMonth.now();
        Random rnd = new Random(7);
        for (int i = months - 1; i >= 0; i--) {
            YearMonth ym = current.minusMonths(i);
            int total = 80 + rnd.nextInt(40);
            int cancelled = 5 + rnd.nextInt(12);
            int noShow = 2 + rnd.nextInt(6);
            result.add(new CancellationStats(ym.toString(), total, cancelled, noShow,
                    Math.round((cancelled + noShow) * 100.0f / total)));
        }
        return ResponseEntity.ok(result);
    }

    /**
     * Revenue forecast based on accepted treatment plans.
     */
    @GetMapping("/revenue-forecast")
    @Operation(summary = "Revenue pipeline from accepted treatment plans")
    public ResponseEntity<RevenueForecast> revenueForecast() {
        // Stub — replace with: SELECT SUM(tp.totalAmount) FROM TreatmentPlan tp WHERE tp.status = 'ACCEPTED'
        return ResponseEntity.ok(new RevenueForecast(
                BigDecimal.valueOf(48500),   // pipeline (ACCEPTED plans)
                BigDecimal.valueOf(23000),   // expected this month
                BigDecimal.valueOf(15200),   // expected next month
                37                           // number of open plans
        ));
    }

    // ─── Response records ─────────────────────────────────────────────────────

    public record MonthlyProduction(String month, BigDecimal production, BigDecimal collected, int appointments) {}
    public record DentistProduction(String dentistName, BigDecimal total, int appointments) {}
    public record ProcedureStats(String code, String name, int count, BigDecimal revenue) {}
    public record CancellationStats(String month, int total, int cancelled, int noShow, int ratePercent) {}
    public record RevenueForecast(BigDecimal pipeline, BigDecimal thisMonth, BigDecimal nextMonth, int openPlans) {}
}
