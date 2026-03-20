package com.dentalclinic.shared;

import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.stream.Collectors;

/**
 * REST controller for daily cash reconciliation (Cuadre de Caja Diario).
 * Round 35 - in-memory stub. Wire with real payment storage in production.
 */
@RestController
@RequestMapping("/api/cash-register")
@Tag(name = "Cash Register", description = "Daily cash reconciliation and closing")
@PreAuthorize("hasAnyRole('ADMIN','DENTIST')")
@CrossOrigin(origins = "*")
public class CashRegisterController {

    private static final DateTimeFormatter DATE_FMT = DateTimeFormatter.ofPattern("yyyy-MM-dd");
    private static final DateTimeFormatter DT_FMT   = DateTimeFormatter.ofPattern("yyyy-MM-dd'T'HH:mm:ss");
    private static final DateTimeFormatter TIME_FMT  = DateTimeFormatter.ofPattern("HH:mm");

    /** Closed sessions keyed by date string */
    private final ConcurrentHashMap<String, ClosedSessionRecord> closedSessions = new ConcurrentHashMap<>();

    // -------------------------------------------------------------------------
    // Stub data - last 5 days of transactions
    // -------------------------------------------------------------------------
    private List<Transaction> generateTransactionsForDate(String date) {
        List<Transaction> txs = new ArrayList<>();
        String[] dentists = {"Dr. García", "Dra. López", "Dr. Martínez"};
        String[] patients = {"Ana Pérez", "Carlos Ruiz", "María Torres", "José Fernández",
                              "Laura Gómez", "Miguel Sánchez", "Elena Díaz", "Pedro Morales"};
        String[] methods  = {"CASH", "CARD", "TRANSFER", "INSURANCE"};
        String[] procs    = {"Empaste", "Limpieza dental", "Extracción", "Ortodoncia revisión",
                              "Corona porcelana", "Endodoncia", "Blanqueamiento", "Implante revisión"};
        String[] times    = {"09:15", "09:45", "10:30", "11:00", "11:45", "12:15", "16:00", "17:30"};
        double[] amounts  = {85.0, 120.0, 65.0, 95.0, 350.0, 220.0, 180.0, 75.0};

        for (int i = 0; i < 8; i++) {
            txs.add(new Transaction(
                UUID.randomUUID(),
                patients[i],
                dentists[i % dentists.length],
                methods[i % methods.length],
                BigDecimal.valueOf(amounts[i]).setScale(2, RoundingMode.HALF_UP),
                times[i],
                procs[i]
            ));
        }
        return txs;
    }

    /** Build closed sessions for last 4 days (today is open) */
    private void ensureHistorySeeded() {
        if (!closedSessions.isEmpty()) return;
        String[] statuses = {"BALANCED", "SURPLUS", "DEFICIT", "BALANCED"};
        String[] closedBy = {"Admin", "Dra. López", "Admin", "Dr. García"};
        for (int d = 4; d >= 1; d--) {
            String date = LocalDate.now().minusDays(d).format(DATE_FMT);
            BigDecimal total = BigDecimal.valueOf(1190.0).setScale(2, RoundingMode.HALF_UP);
            closedSessions.put(date, new ClosedSessionRecord(
                date, total, statuses[d - 1], closedBy[d - 1],
                LocalDate.now().minusDays(d).atTime(19, 0).format(DT_FMT),
                ""
            ));
        }
    }

    // -------------------------------------------------------------------------
    // GET /api/cash-register/summary?date=YYYY-MM-DD
    // -------------------------------------------------------------------------
    @GetMapping("/summary")
    public ResponseEntity<DailySummary> getSummary(@RequestParam(required = false) String date) {
        ensureHistorySeeded();
        String targetDate = (date != null && !date.isBlank()) ? date : LocalDate.now().format(DATE_FMT);
        List<Transaction> txs = generateTransactionsForDate(targetDate);

        BigDecimal totalCash     = sum(txs, "CASH");
        BigDecimal totalCard     = sum(txs, "CARD");
        BigDecimal totalTransfer = sum(txs, "TRANSFER");
        BigDecimal totalInsurance= sum(txs, "INSURANCE");
        BigDecimal grandTotal    = totalCash.add(totalCard).add(totalTransfer).add(totalInsurance);

        // By dentist
        Map<String, List<Transaction>> byDentist = txs.stream()
            .collect(Collectors.groupingBy(Transaction::dentistName));
        List<DentistSummary> dentistSummaries = byDentist.entrySet().stream()
            .map(e -> new DentistSummary(
                e.getKey(),
                e.getValue().stream().map(Transaction::amount)
                    .reduce(BigDecimal.ZERO, BigDecimal::add).setScale(2, RoundingMode.HALF_UP),
                e.getValue().size()))
            .collect(Collectors.toList());

        // By insurance (only INSURANCE transactions)
        List<Transaction> insuranceTxs = txs.stream()
            .filter(t -> "INSURANCE".equals(t.method())).collect(Collectors.toList());
        List<InsuranceSummary> insuranceSummaries = List.of(
            new InsuranceSummary("Adeslas", totalInsurance, insuranceTxs.size())
        );

        ClosedSessionRecord closed = closedSessions.get(targetDate);
        boolean isClosed = closed != null;
        String closedAt = isClosed ? closed.closedAt() : null;
        String closedBy = isClosed ? closed.closedBy() : null;

        return ResponseEntity.ok(new DailySummary(
            targetDate, totalCash, totalCard, totalTransfer, totalInsurance, grandTotal,
            txs.size(), dentistSummaries, insuranceSummaries, isClosed, closedAt, closedBy
        ));
    }

    // -------------------------------------------------------------------------
    // POST /api/cash-register/close
    // -------------------------------------------------------------------------
    @PostMapping("/close")
    public ResponseEntity<CloseResponse> closeRegister(@RequestBody CloseRequest req) {
        ensureHistorySeeded();
        String targetDate = (req.date() != null && !req.date().isBlank())
            ? req.date() : LocalDate.now().format(DATE_FMT);
        List<Transaction> txs = generateTransactionsForDate(targetDate);
        BigDecimal systemTotal = txs.stream().map(Transaction::amount)
            .reduce(BigDecimal.ZERO, BigDecimal::add).setScale(2, RoundingMode.HALF_UP);

        BigDecimal physical = req.physicalCashCount() != null
            ? req.physicalCashCount() : BigDecimal.ZERO;
        BigDecimal difference = physical.subtract(systemTotal).setScale(2, RoundingMode.HALF_UP);
        String status;
        if (difference.abs().compareTo(BigDecimal.ONE) < 0) status = "BALANCED";
        else if (difference.compareTo(BigDecimal.ZERO) > 0)  status = "SURPLUS";
        else                                                   status = "DEFICIT";

        String closedAt = LocalDateTime.now().format(DT_FMT);
        String closedBy = req.closedBy() != null ? req.closedBy() : "Admin";
        closedSessions.put(targetDate, new ClosedSessionRecord(
            targetDate, systemTotal, status, closedBy, closedAt, req.notes() != null ? req.notes() : ""
        ));

        return ResponseEntity.ok(new CloseResponse(
            targetDate, systemTotal, physical, difference, status, closedAt
        ));
    }

    // -------------------------------------------------------------------------
    // GET /api/cash-register/history?months=3
    // -------------------------------------------------------------------------
    @GetMapping("/history")
    public ResponseEntity<List<ClosedSession>> getHistory(
            @RequestParam(defaultValue = "3") int months) {
        ensureHistorySeeded();
        List<ClosedSession> result = closedSessions.values().stream()
            .sorted(Comparator.comparing(ClosedSessionRecord::date).reversed())
            .map(r -> new ClosedSession(r.date(), r.total(), r.status(), r.closedBy(), r.closedAt()))
            .collect(Collectors.toList());
        return ResponseEntity.ok(result);
    }

    // -------------------------------------------------------------------------
    // GET /api/cash-register/transactions?date=YYYY-MM-DD
    // -------------------------------------------------------------------------
    @GetMapping("/transactions")
    public ResponseEntity<List<Transaction>> getTransactions(
            @RequestParam(required = false) String date) {
        String targetDate = (date != null && !date.isBlank()) ? date : LocalDate.now().format(DATE_FMT);
        return ResponseEntity.ok(generateTransactionsForDate(targetDate));
    }

    // -------------------------------------------------------------------------
    // Helpers
    // -------------------------------------------------------------------------
    private BigDecimal sum(List<Transaction> txs, String method) {
        return txs.stream()
            .filter(t -> method.equals(t.method()))
            .map(Transaction::amount)
            .reduce(BigDecimal.ZERO, BigDecimal::add)
            .setScale(2, RoundingMode.HALF_UP);
    }

    // -------------------------------------------------------------------------
    // Records / DTOs
    // -------------------------------------------------------------------------
    public record DailySummary(
        String date,
        BigDecimal totalCash,
        BigDecimal totalCard,
        BigDecimal totalTransfer,
        BigDecimal totalInsurance,
        BigDecimal grandTotal,
        int transactionCount,
        List<DentistSummary> byDentist,
        List<InsuranceSummary> byInsurance,
        boolean closed,
        String closedAt,
        String closedBy
    ) {}

    public record DentistSummary(String dentistName, BigDecimal total, int count) {}

    public record InsuranceSummary(String insuranceName, BigDecimal total, int count) {}

    public record CloseRequest(
        String date, String closedBy, String notes, BigDecimal physicalCashCount
    ) {}

    public record CloseResponse(
        String date,
        BigDecimal systemTotal,
        BigDecimal physicalCount,
        BigDecimal difference,
        String status,
        String closedAt
    ) {}

    public record ClosedSession(
        String date, BigDecimal total, String status, String closedBy, String closedAt
    ) {}

    public record Transaction(
        UUID id, String patientName, String dentistName, String method,
        BigDecimal amount, String time, String procedure
    ) {}

    private record ClosedSessionRecord(
        String date, BigDecimal total, String status, String closedBy,
        String closedAt, String notes
    ) {}
}
