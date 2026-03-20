package com.dentalclinic.shared;

import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.util.List;
import java.util.UUID;

@RestController
@RequestMapping("/api/treatment-plans")
@Tag(name = "Treatment Plans", description = "Patient treatment plan and budget management")
public class TreatmentPlanController {

    private final TreatmentPlanRepository planRepo;
    private final TreatmentPlanItemRepository itemRepo;

    public TreatmentPlanController(TreatmentPlanRepository planRepo,
                                    TreatmentPlanItemRepository itemRepo) {
        this.planRepo = planRepo;
        this.itemRepo = itemRepo;
    }

    @GetMapping("/patient/{patientId}")
    @Operation(summary = "List all treatment plans for a patient")
    public ResponseEntity<List<TreatmentPlan>> listByPatient(@PathVariable UUID patientId) {
        return ResponseEntity.ok(planRepo.findByPatientIdOrderByCreatedAtDesc(patientId));
    }

    @GetMapping("/{id}/items")
    @Operation(summary = "Get items for a treatment plan")
    public ResponseEntity<List<TreatmentPlanItem>> getItems(@PathVariable UUID id) {
        return ResponseEntity.ok(itemRepo.findByPlanIdOrderByToothNumber(id));
    }

    @PostMapping
    @Operation(summary = "Create a new treatment plan with items")
    public ResponseEntity<TreatmentPlan> create(@RequestBody @Valid TreatmentPlanRequest req) {
        TreatmentPlan plan = new TreatmentPlan(
                req.patientId(), req.dentistId(), req.expiresAt(), req.notes());
        plan = planRepo.save(plan);

        BigDecimal total = BigDecimal.ZERO;
        for (var item : req.items()) {
            TreatmentPlanItem tpi = new TreatmentPlanItem(
                    plan.getId(), item.toothNumber(), item.procedureCode(),
                    item.description(), item.quantity(), item.unitPrice(),
                    item.insuranceCoverage());
            itemRepo.save(tpi);
            total = total.add(tpi.getTotalPrice());
        }

        plan.setTotalAmount(total);
        return ResponseEntity.ok(planRepo.save(plan));
    }

    @PatchMapping("/{id}/status")
    @Operation(summary = "Update treatment plan status")
    public ResponseEntity<TreatmentPlan> updateStatus(
            @PathVariable UUID id,
            @RequestBody StatusRequest req) {
        return planRepo.findById(id).map(plan -> {
            plan.setStatus(req.status());
            return ResponseEntity.ok(planRepo.save(plan));
        }).orElse(ResponseEntity.notFound().build());
    }

    @DeleteMapping("/{id}")
    @Operation(summary = "Delete a draft treatment plan")
    public ResponseEntity<Void> delete(@PathVariable UUID id) {
        itemRepo.deleteByPlanId(id);
        planRepo.deleteById(id);
        return ResponseEntity.noContent().build();
    }

    public record TreatmentPlanRequest(
            UUID patientId,
            UUID dentistId,
            LocalDate expiresAt,
            String notes,
            List<ItemRequest> items) {}

    public record ItemRequest(
            Integer toothNumber,
            String procedureCode,
            String description,
            Integer quantity,
            BigDecimal unitPrice,
            BigDecimal insuranceCoverage) {}

    public record StatusRequest(String status) {}
}
