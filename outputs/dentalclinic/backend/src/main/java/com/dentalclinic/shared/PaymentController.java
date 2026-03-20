package com.dentalclinic.shared;

import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.stream.Collectors;

/**
 * Payment history and point-of-sale (TPV) controller.
 * Round 29 — in-memory stub; wire with real persistence in production.
 */
@RestController
@RequestMapping("/api/payments")
@Tag(name = "Payments", description = "Payment history and point of sale")
@PreAuthorize("hasAnyRole('ADMIN','DENTIST')")
public class PaymentController {

    private static final Map<UUID, PaymentResponse> STORE = new ConcurrentHashMap<>();

    static {
        String[][] demo = {
            {"a1b2c3d4-0001-0001-0001-000000000001","Ana López","f1000001-0000-0000-0000-000000000001","120.00","CASH","","PAID","2026-03-01T09:15:00","Limpieza dental"},
            {"a1b2c3d4-0002-0002-0002-000000000002","Carlos Ruiz","f1000002-0000-0000-0000-000000000002","350.00","CARD","TXN-4821","PAID","2026-03-03T10:30:00","Empaste molar"},
            {"a1b2c3d4-0003-0003-0003-000000000003","María García","f1000003-0000-0000-0000-000000000003","80.00","INSURANCE","SEG-001","PAID","2026-03-05T11:00:00","Revisión periódica"},
            {"a1b2c3d4-0004-0004-0004-000000000004","Pedro Sánchez","f1000004-0000-0000-0000-000000000004","900.00","TRANSFER","TRAN-9910","PAID","2026-03-07T12:45:00","Corona porcelana"},
            {"a1b2c3d4-0005-0005-0005-000000000005","Laura Martínez","f1000005-0000-0000-0000-000000000005","200.00","CARD","TXN-5533","PAID","2026-03-10T09:00:00","Blanqueamiento"},
            {"a1b2c3d4-0006-0006-0006-000000000006","Javier Torres","f1000006-0000-0000-0000-000000000006","45.00","CASH","","PAID","2026-03-12T14:20:00","Urgencia dolor"},
            {"a1b2c3d4-0007-0007-0007-000000000007","Sofía Díaz","f1000007-0000-0000-0000-000000000007","1200.00","INSURANCE","SEG-082","PAID","2026-03-14T16:00:00","Ortodoncia mensualidad"},
            {"a1b2c3d4-0008-0008-0008-000000000008","Miguel Fernández","f1000008-0000-0000-0000-000000000008","75.00","CASH","","PAID","2026-03-17T08:30:00","Radiografía panorámica"},
            {"a1b2c3d4-0009-0009-0009-000000000009","Elena Romero","f1000009-0000-0000-0000-000000000009","500.00","CARD","TXN-7741","PAID","2026-03-19T10:10:00","Implante fase 1"},
            {"a1b2c3d4-0010-0010-0010-000000000010","Roberto Jiménez","f1000010-0000-0000-0000-000000000010","160.00","TRANSFER","TRAN-3301","PAID","2026-03-19T11:45:00","Endodoncia"}
        };
        for (String[] d : demo) {
            UUID id = UUID.randomUUID();
            STORE.put(id, new PaymentResponse(
                id,
                UUID.fromString(d[0]), d[1],
                UUID.fromString(d[2]),
                new BigDecimal(d[3]), d[4], d[5], d[6], d[7], d[8]
            ));
        }
    }

    /** GET /api/payments/patient/{patientId} */
    @GetMapping("/patient/{patientId}")
    @Operation(summary = "Historial de pagos de un paciente")
    public ResponseEntity<List<PaymentResponse>> getByPatient(@PathVariable UUID patientId) {
        List<PaymentResponse> result = STORE.values().stream()
                .filter(p -> p.patientId().equals(patientId))
                .sorted(Comparator.comparing(PaymentResponse::createdAt).reversed())
                .collect(Collectors.toList());
        return ResponseEntity.ok(result);
    }

    /** POST /api/payments */
    @PostMapping
    @Operation(summary = "Registrar un pago")
    public ResponseEntity<PaymentResponse> createPayment(@RequestBody PaymentRequest req) {
        UUID id = UUID.randomUUID();
        String now = LocalDateTime.now().format(DateTimeFormatter.ISO_LOCAL_DATE_TIME);
        PaymentResponse saved = new PaymentResponse(
                id, req.patientId(), "Paciente", req.invoiceId(),
                req.amount(), req.method(),
                req.reference() != null ? req.reference() : "",
                "PAID", now,
                req.notes() != null ? req.notes() : ""
        );
        STORE.put(id, saved);
        return ResponseEntity.ok(saved);
    }

    /** GET /api/payments/summary/today */
    @GetMapping("/summary/today")
    @Operation(summary = "Resumen de caja del día")
    public ResponseEntity<DailySummary> getTodaySummary() {
        LocalDate today = LocalDate.now();
        DateTimeFormatter fmt = DateTimeFormatter.ISO_LOCAL_DATE_TIME;
        List<PaymentResponse> todayPayments = STORE.values().stream()
                .filter(p -> {
                    try { return LocalDateTime.parse(p.createdAt(), fmt).toLocalDate().equals(today); }
                    catch (Exception e) { return false; }
                })
                .collect(Collectors.toList());
        BigDecimal total = BigDecimal.ZERO, cash = BigDecimal.ZERO,
                   card  = BigDecimal.ZERO, transfer = BigDecimal.ZERO, insurance = BigDecimal.ZERO;
        for (PaymentResponse p : todayPayments) {
            total = total.add(p.amount());
            switch (p.method()) {
                case "CASH"     -> cash     = cash.add(p.amount());
                case "CARD"     -> card     = card.add(p.amount());
                case "TRANSFER" -> transfer = transfer.add(p.amount());
                case "INSURANCE"-> insurance= insurance.add(p.amount());
            }
        }
        return ResponseEntity.ok(new DailySummary(today, total, cash, card, transfer, insurance, todayPayments.size()));
    }

    /** GET /api/payments/summary/monthly?months=6 */
    @GetMapping("/summary/monthly")
    @Operation(summary = "Ingresos mensuales por método de pago")
    public ResponseEntity<List<MonthlyPaymentSummary>> getMonthlySummary(
            @RequestParam(defaultValue = "6") int months) {
        DateTimeFormatter fmt = DateTimeFormatter.ISO_LOCAL_DATE_TIME;
        DateTimeFormatter monthFmt = DateTimeFormatter.ofPattern("yyyy-MM");
        LocalDate cutoff = LocalDate.now().minusMonths(months - 1L).withDayOfMonth(1);
        Map<String, MonthlyPaymentSummary> grouped = new LinkedHashMap<>();
        STORE.values().stream()
                .filter(p -> {
                    try { return !LocalDateTime.parse(p.createdAt(), fmt).toLocalDate().isBefore(cutoff); }
                    catch (Exception e) { return false; }
                })
                .forEach(p -> {
                    String month;
                    try { month = LocalDateTime.parse(p.createdAt(), fmt).format(monthFmt); }
                    catch (Exception e) { month = "unknown"; }
                    grouped.compute(month, (k, ex) -> {
                        if (ex == null) ex = new MonthlyPaymentSummary(k, BigDecimal.ZERO, BigDecimal.ZERO,
                                BigDecimal.ZERO, BigDecimal.ZERO, BigDecimal.ZERO);
                        return new MonthlyPaymentSummary(k,
                            ex.total().add(p.amount()),
                            ex.cash().add("CASH".equals(p.method())      ? p.amount() : BigDecimal.ZERO),
                            ex.card().add("CARD".equals(p.method())      ? p.amount() : BigDecimal.ZERO),
                            ex.transfer().add("TRANSFER".equals(p.method())  ? p.amount() : BigDecimal.ZERO),
                            ex.insurance().add("INSURANCE".equals(p.method()) ? p.amount() : BigDecimal.ZERO));
                    });
                });
        List<MonthlyPaymentSummary> result = new ArrayList<>(grouped.values());
        result.sort(Comparator.comparing(MonthlyPaymentSummary::month));
        return ResponseEntity.ok(result);
    }

    public record PaymentRequest(
            UUID patientId,
            UUID invoiceId,
            BigDecimal amount,
            String method,
            String reference,
            String notes
    ) {}

    public record PaymentResponse(
            UUID id,
            UUID patientId,
            String patientName,
            UUID invoiceId,
            BigDecimal amount,
            String method,
            String reference,
            String status,
            String createdAt,
            String notes
    ) {}

    public record DailySummary(
            LocalDate date,
            BigDecimal total,
            BigDecimal cash,
            BigDecimal card,
            BigDecimal transfer,
            BigDecimal insurance,
            int count
    ) {}

    public record MonthlyPaymentSummary(
            String month,
            BigDecimal total,
            BigDecimal cash,
            BigDecimal card,
            BigDecimal transfer,
            BigDecimal insurance
    ) {}
}
