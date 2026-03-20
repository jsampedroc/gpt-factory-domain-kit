package com.dentalclinic.shared;

import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDate;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.stream.Collectors;

@RestController
@RequestMapping("/api/nps")
public class NpsController {

    record NpsSurvey(String id, String patientId, String patientName, String dentistName,
                     int score, String comment, String category, String date) {}
    record NpsStats(double npsScore, int promoters, int passives, int detractors, int total,
                    Map<String, Double> categoryAverages) {}

    private final Map<String, NpsSurvey> surveys = new ConcurrentHashMap<>();

    public NpsController() {
        String[] patients = {"García López, Ana", "Fernández Ruiz, Pedro", "Sánchez Torres, Luis",
                "Morales Vega, Carmen", "Jiménez Castro, Rosa", "Rodríguez Pérez, Juan",
                "López Martín, Elena", "González Díaz, Miguel", "Hernández Ruiz, Sofía",
                "Martínez López, Carlos", "Torres Sánchez, Isabel", "Flores Moreno, David"};
        String[] dentists = {"Dr. Martínez", "Dra. Romero", "Dr. Navarro"};
        String[] categories = {"INSTALACIONES", "ATENCION", "TIEMPO_ESPERA", "RESULTADO_TRATAMIENTO", "PRECIO"};
        int[] scores = {10, 9, 8, 10, 7, 9, 6, 10, 8, 9, 5, 10};
        String[] comments = {
            "Excelente atención, muy profesional",
            "Muy satisfecho con el resultado",
            "Buena clínica, algo de espera",
            "El mejor dentista que he tenido",
            "Buen trato pero instalaciones mejorables",
            "Muy cómodo y rápido el tratamiento",
            "Regular, tuve que esperar bastante",
            "Recomendaré a toda mi familia",
            "Buen servicio en general",
            "La Dra. Romero es fantástica",
            "Precio algo elevado",
            "Volveré sin dudarlo"
        };
        for (int i = 0; i < patients.length; i++) {
            String id = "nps" + (i + 1);
            LocalDate date = LocalDate.now().minusDays(patients.length - i);
            surveys.put(id, new NpsSurvey(id, "p" + (i + 1), patients[i],
                    dentists[i % dentists.length], scores[i], comments[i],
                    categories[i % categories.length], date.toString()));
        }
    }

    @GetMapping
    @PreAuthorize("hasAnyRole('ADMIN','DENTIST')")
    public List<NpsSurvey> listAll(
            @RequestParam(required = false) String from,
            @RequestParam(required = false) String to) {
        return surveys.values().stream()
                .filter(s -> from == null || s.date().compareTo(from) >= 0)
                .filter(s -> to == null || s.date().compareTo(to) <= 0)
                .sorted(Comparator.comparing(NpsSurvey::date).reversed())
                .collect(Collectors.toList());
    }

    @GetMapping("/stats")
    @PreAuthorize("hasAnyRole('ADMIN','DENTIST')")
    public NpsStats stats() {
        List<NpsSurvey> all = new ArrayList<>(surveys.values());
        int total = all.size();
        long promoters = all.stream().filter(s -> s.score() >= 9).count();
        long detractors = all.stream().filter(s -> s.score() <= 6).count();
        long passives = total - promoters - detractors;
        double nps = total == 0 ? 0 : ((double)(promoters - detractors) / total) * 100;
        Map<String, Double> catAvg = all.stream()
                .collect(Collectors.groupingBy(NpsSurvey::category,
                        Collectors.averagingInt(NpsSurvey::score)));
        return new NpsStats(Math.round(nps * 10.0) / 10.0,
                (int) promoters, (int) passives, (int) detractors, total, catAvg);
    }

    @PostMapping
    public NpsSurvey submitSurvey(@RequestBody NpsSurvey req) {
        String id = "nps" + UUID.randomUUID().toString().substring(0, 8);
        NpsSurvey s = new NpsSurvey(id, req.patientId(), req.patientName(), req.dentistName(),
                req.score(), req.comment(), req.category(), LocalDate.now().toString());
        surveys.put(id, s);
        return s;
    }
}
