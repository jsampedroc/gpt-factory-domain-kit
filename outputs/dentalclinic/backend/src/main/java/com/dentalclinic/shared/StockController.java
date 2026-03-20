package com.dentalclinic.shared;

import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.stream.Collectors;

/**
 * Clinic supply and inventory management.
 * Pre-populated with 15 realistic dental supplies.
 * In production, replace in-memory store with a JPA repository.
 */
@RestController
@RequestMapping("/api/stock")
@Tag(name = "Stock", description = "Clinic supply and inventory management")
@PreAuthorize("hasAnyRole('ADMIN')")
public class StockController {

    // ---------------------------------------------------------------
    // In-memory store
    // ---------------------------------------------------------------

    private final ConcurrentHashMap<UUID, StockItem> store = new ConcurrentHashMap<>();
    private final ConcurrentHashMap<UUID, List<StockMovement>> movements = new ConcurrentHashMap<>();

    public StockController() {
        seed();
    }

    private void seed() {
        addItem("Anestesia Articaína 4%",            "Anestésicos",              "cartucho",      20,  120, new BigDecimal("1.85"),   "DentalDep S.L.");
        addItem("Guantes de nitrilo (S)",             "EPIs",                     "caja 100u",      5,   22, new BigDecimal("7.50"),   "Medistock S.A.");
        addItem("Guantes de nitrilo (M)",             "EPIs",                     "caja 100u",      5,   18, new BigDecimal("7.50"),   "Medistock S.A.");
        addItem("Guantes de nitrilo (L)",             "EPIs",                     "caja 100u",      5,    4, new BigDecimal("7.50"),   "Medistock S.A.");
        addItem("Mascarillas FFP2",                   "EPIs",                     "caja 20u",      10,   35, new BigDecimal("12.00"),  "Medistock S.A.");
        addItem("Gasas estériles",                    "Material quirúrgico",      "paquete 100u",   8,   50, new BigDecimal("4.20"),   "SurgePro");
        addItem("Implante Nobel Biocare Ø3.5",        "Implantes",                "unidad",         5,   12, new BigDecimal("185.00"), "Nobel Biocare");
        addItem("Composite Filtek Z350",              "Resinas",                  "jeringa 4g",     6,   20, new BigDecimal("28.50"),  "3M ESPE");
        addItem("Cemento ionómero de vidrio",         "Cementos",                 "polvo 25g",      4,   10, new BigDecimal("34.00"),  "GC Europe");
        addItem("Fresas de diamante redondas",        "Instrumental rotatorio",   "caja 10u",       3,    8, new BigDecimal("19.90"),  "Komet Dental");
        addItem("Papel de articular 200µm",           "Diagnóstico",              "caja 144 tiras", 2,    6, new BigDecimal("5.80"),   "Bausch");
        addItem("Hilo de retracción #2",              "Prótesis",                 "carrete",        3,    5, new BigDecimal("11.40"),  "Ultrapak");
        addItem("Ácido grabador 37%",                 "Adhesivos",                "jeringa 3ml",    5,   14, new BigDecimal("6.20"),   "Ivoclar");
        addItem("Adhesivo Optibond FL",               "Adhesivos",                "kit",            3,    0, new BigDecimal("62.00"),  "Kerr Dental");
        addItem("Sutura reabsorbible 3/0",            "Material quirúrgico",      "caja 12u",       4,    9, new BigDecimal("22.50"),  "Ethicon");
    }

    private void addItem(String name, String category, String unit,
                         int minStock, int currentStock, BigDecimal unitPrice, String supplier) {
        UUID id = UUID.randomUUID();
        String status = computeStatus(currentStock, minStock);
        store.put(id, new StockItem(id, name, category, unit, minStock, currentStock, unitPrice, supplier, status));
        movements.put(id, new ArrayList<>());
    }

    private String computeStatus(int current, int min) {
        if (current == 0)     return "CRITICAL";
        if (current <= min)   return "LOW";
        return "OK";
    }

    // ---------------------------------------------------------------
    // Endpoints
    // ---------------------------------------------------------------

    @GetMapping
    @Operation(summary = "Listar todos los artículos (con filtro opcional ?search=)")
    public ResponseEntity<List<StockItem>> list(@RequestParam(required = false) String search) {
        List<StockItem> items = new ArrayList<>(store.values());
        if (search != null && !search.isBlank()) {
            String q = search.toLowerCase();
            items = items.stream()
                    .filter(i -> i.name().toLowerCase().contains(q)
                              || i.category().toLowerCase().contains(q)
                              || i.supplier().toLowerCase().contains(q))
                    .collect(Collectors.toList());
        }
        items.sort(Comparator.comparing(StockItem::name));
        return ResponseEntity.ok(items);
    }

    @PostMapping
    @Operation(summary = "Añadir nuevo artículo al stock")
    public ResponseEntity<StockItem> create(@RequestBody StockItemRequest req) {
        UUID id = UUID.randomUUID();
        String status = computeStatus(req.currentStock(), req.minStock());
        StockItem item = new StockItem(id, req.name(), req.category(), req.unit(),
                req.minStock(), req.currentStock(), req.unitPrice(), req.supplier(), status);
        store.put(id, item);
        movements.put(id, new ArrayList<>());
        return ResponseEntity.ok(item);
    }

    @PutMapping("/{id}")
    @Operation(summary = "Actualizar datos de un artículo")
    public ResponseEntity<StockItem> update(@PathVariable UUID id,
                                            @RequestBody StockItemRequest req) {
        StockItem existing = store.get(id);
        if (existing == null) return ResponseEntity.notFound().build();
        String status = computeStatus(req.currentStock(), req.minStock());
        StockItem updated = new StockItem(id, req.name(), req.category(), req.unit(),
                req.minStock(), req.currentStock(), req.unitPrice(), req.supplier(), status);
        store.put(id, updated);
        return ResponseEntity.ok(updated);
    }

    @PostMapping("/{id}/movement")
    @Operation(summary = "Registrar movimiento de stock (ENTRADA / SALIDA)")
    public ResponseEntity<StockItem> recordMovement(@PathVariable UUID id,
                                                    @RequestBody MovementRequest req) {
        StockItem item = store.get(id);
        if (item == null) return ResponseEntity.notFound().build();

        int newStock = "IN".equalsIgnoreCase(req.type())
                ? item.currentStock() + req.quantity()
                : Math.max(0, item.currentStock() - req.quantity());

        StockMovement mov = new StockMovement(
                UUID.randomUUID(), id, req.type().toUpperCase(), req.quantity(), req.reason(),
                LocalDateTime.now().format(DateTimeFormatter.ISO_LOCAL_DATE_TIME));
        movements.computeIfAbsent(id, k -> new ArrayList<>()).add(mov);

        String status = computeStatus(newStock, item.minStock());
        StockItem updated = new StockItem(id, item.name(), item.category(), item.unit(),
                item.minStock(), newStock, item.unitPrice(), item.supplier(), status);
        store.put(id, updated);
        return ResponseEntity.ok(updated);
    }

    @GetMapping("/low")
    @Operation(summary = "Artículos con stock bajo o crítico (alertas)")
    public ResponseEntity<List<StockItem>> lowStock() {
        List<StockItem> alerts = store.values().stream()
                .filter(i -> !"OK".equals(i.status()))
                .sorted(Comparator.comparing(StockItem::name))
                .collect(Collectors.toList());
        return ResponseEntity.ok(alerts);
    }

    @GetMapping("/{id}/movements")
    @Operation(summary = "Historial de movimientos de un artículo")
    public ResponseEntity<List<StockMovement>> getMovements(@PathVariable UUID id) {
        List<StockMovement> list = movements.getOrDefault(id, Collections.emptyList());
        List<StockMovement> sorted = new ArrayList<>(list);
        sorted.sort(Comparator.comparing(StockMovement::createdAt).reversed());
        return ResponseEntity.ok(sorted);
    }

    // ---------------------------------------------------------------
    // Inner record types
    // ---------------------------------------------------------------

    public record StockItem(
            UUID id,
            String name,
            String category,
            String unit,
            int minStock,
            int currentStock,
            BigDecimal unitPrice,
            String supplier,
            String status          // OK | LOW | CRITICAL
    ) {}

    public record StockItemRequest(
            String name,
            String category,
            String unit,
            int minStock,
            int currentStock,
            BigDecimal unitPrice,
            String supplier
    ) {}

    public record StockMovement(
            UUID id,
            UUID itemId,
            String type,           // IN | OUT
            int quantity,
            String reason,
            String createdAt
    ) {}

    public record MovementRequest(
            String type,           // IN | OUT
            int quantity,
            String reason
    ) {}
}
