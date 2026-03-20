package com.dentalclinic.shared;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDate;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.stream.Collectors;

@RestController
@RequestMapping("/api/previsit-forms")
public class PreVisitFormController {

    record PreVisitForm(String id, String patientId, String patientName, String appointmentId,
                        String date, String status,
                        // Anamnesis rápida
                        List<String> allergies, List<String> currentMedications,
                        List<String> medicalConditions,
                        // Motivo de visita
                        String chiefComplaint, String painScale, String painLocation,
                        String painSince, String painType,
                        // Hábitos
                        boolean smoker, boolean alcoholConsumer, boolean bruxism,
                        // Consentimiento digital
                        boolean gdprConsent, boolean treatmentConsent,
                        String submittedAt, String ipAddress) {}

    record FormTemplate(String id, String name, String description, List<String> sections) {}

    private final Map<String, PreVisitForm> forms = new ConcurrentHashMap<>();

    public PreVisitFormController() {
        forms.put("f1", new PreVisitForm("f1","p1","García López, Ana","apt1",
                LocalDate.now().minusDays(2).toString(),"COMPLETED",
                List.of("Penicilina"), List.of("Ibuprofeno 400mg"),
                List.of("Hipertensión"),
                "Dolor muela del juicio","7","inferior derecho","3 días","Pulsátil",
                false, false, true,
                true, true,
                LocalDate.now().minusDays(2)+"T18:30","192.168.1.10"));
        forms.put("f2", new PreVisitForm("f2","p2","Fernández Ruiz, Pedro","apt2",
                LocalDate.now().minusDays(1).toString(),"COMPLETED",
                List.of(), List.of(),
                List.of("Diabetes tipo 2"),
                "Revisión ortodoncia","0","N/A","Sin dolor","Sin dolor",
                true, false, false,
                true, true,
                LocalDate.now().minusDays(1)+"T09:15","192.168.1.22"));
        forms.put("f3", new PreVisitForm("f3","p3","Sánchez Torres, Luis","apt3",
                LocalDate.now().toString(),"PENDING",
                null, null, null, null, null, null, null, null,
                false, false, false, false, false, null, null));
    }

    @GetMapping
    public List<PreVisitForm> listAll(@RequestParam(required = false) String status) {
        return forms.values().stream()
                .filter(f -> status == null || f.status().equals(status))
                .sorted(Comparator.comparing(PreVisitForm::date).reversed())
                .collect(Collectors.toList());
    }

    @GetMapping("/{id}")
    public ResponseEntity<PreVisitForm> getById(@PathVariable String id) {
        return Optional.ofNullable(forms.get(id))
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    @GetMapping("/patient/{patientId}")
    public List<PreVisitForm> byPatient(@PathVariable String patientId) {
        return forms.values().stream()
                .filter(f -> f.patientId().equals(patientId))
                .sorted(Comparator.comparing(PreVisitForm::date).reversed())
                .collect(Collectors.toList());
    }

    @PostMapping
    public PreVisitForm create(@RequestBody PreVisitForm req) {
        String id = "f" + UUID.randomUUID().toString().substring(0, 8);
        PreVisitForm f = new PreVisitForm(id, req.patientId(), req.patientName(), req.appointmentId(),
                LocalDate.now().toString(), "PENDING",
                null, null, null, null, null, null, null, null,
                false, false, false, false, false, null, null);
        forms.put(id, f);
        return f;
    }

    @PutMapping("/{id}/submit")
    public ResponseEntity<PreVisitForm> submit(
            @PathVariable String id, @RequestBody PreVisitForm req) {
        PreVisitForm existing = forms.get(id);
        if (existing == null) return ResponseEntity.notFound().build();
        PreVisitForm updated = new PreVisitForm(id, existing.patientId(), existing.patientName(),
                existing.appointmentId(), existing.date(), "COMPLETED",
                req.allergies(), req.currentMedications(), req.medicalConditions(),
                req.chiefComplaint(), req.painScale(), req.painLocation(),
                req.painSince(), req.painType(),
                req.smoker(), req.alcoholConsumer(), req.bruxism(),
                req.gdprConsent(), req.treatmentConsent(),
                LocalDate.now()+"T"+java.time.LocalTime.now().toString().substring(0,5), "");
        forms.put(id, updated);
        return ResponseEntity.ok(updated);
    }

    @GetMapping("/templates")
    public List<FormTemplate> templates() {
        return List.of(
            new FormTemplate("tpl1","Formulario estándar","Anamnesis + motivo visita + hábitos + consentimientos",
                    List.of("ALERGIAS","MEDICACION","ENFERMEDADES","MOTIVO_VISITA","HABITOS","CONSENTIMIENTOS")),
            new FormTemplate("tpl2","Formulario rápido","Solo motivo de visita y consentimiento RGPD",
                    List.of("MOTIVO_VISITA","CONSENTIMIENTOS")),
            new FormTemplate("tpl3","Primera visita completa","Historial médico completo",
                    List.of("ALERGIAS","MEDICACION","ENFERMEDADES","ANTECEDENTES","MOTIVO_VISITA","HABITOS","CONSENTIMIENTOS","RGPD"))
        );
    }

    @GetMapping("/stats")
    public Map<String, Object> stats() {
        List<PreVisitForm> all = new ArrayList<>(forms.values());
        Map<String, Object> result = new LinkedHashMap<>();
        result.put("total", all.size());
        result.put("pending", all.stream().filter(f -> "PENDING".equals(f.status())).count());
        result.put("completed", all.stream().filter(f -> "COMPLETED".equals(f.status())).count());
        result.put("gdprConsentRate", all.stream().filter(f -> Boolean.TRUE.equals(f.gdprConsent())).count() * 100.0 / Math.max(all.size(), 1));
        return result;
    }
}
