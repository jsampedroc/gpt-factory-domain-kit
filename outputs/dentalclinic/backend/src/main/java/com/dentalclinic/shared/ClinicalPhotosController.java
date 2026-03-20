package com.dentalclinic.shared;

import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.stream.Collectors;

/**
 * REST controller for clinical photo gallery (before/after, X-rays, intraoral).
 * Round 32 - in-memory implementation. Wire with real storage in production.
 */
@RestController
@RequestMapping("/api/clinical-photos")
@Tag(name = "Clinical Photos", description = "Patient clinical photo gallery")
@PreAuthorize("hasAnyRole('ADMIN','DENTIST')")
@CrossOrigin(origins = "*")
public class ClinicalPhotosController {

    private final ConcurrentHashMap<UUID, List<ClinicalPhoto>> store = new ConcurrentHashMap<>();

    private static final UUID DEMO_PATIENT_1 = UUID.fromString("00000000-0000-0000-0000-000000000001");
    private static final UUID DEMO_PATIENT_2 = UUID.fromString("00000000-0000-0000-0000-000000000002");

    public ClinicalPhotosController() {
        store.put(DEMO_PATIENT_1, buildDemoPhotos(DEMO_PATIENT_1));
        store.put(DEMO_PATIENT_2, buildDemoPhotos(DEMO_PATIENT_2));
    }

    private List<ClinicalPhoto> buildDemoPhotos(UUID patientId) {
        List<ClinicalPhoto> photos = new ArrayList<>();
        String[][] demo = {
            {"BEFORE",    "11", "Estado inicial incisivo central",    "/api/clinical-photos/demo/1.jpg", "INITIAL"},
            {"AFTER",     "11", "Post tratamiento incisivo central",  "/api/clinical-photos/demo/2.jpg", "FINAL"},
            {"XRAY",      "36", "Radiografia molar inferior",         "/api/clinical-photos/demo/3.jpg", "PROGRESS"},
            {"PANORAMIC", "",   "Ortopantomografia completa",         "/api/clinical-photos/demo/4.jpg", "INITIAL"},
            {"INTRAORAL", "21", "Vista intraoral lateral",            "/api/clinical-photos/demo/5.jpg", "PROGRESS"},
            {"OTHER",     "46", "Foto de seguimiento",                "/api/clinical-photos/demo/6.jpg", "EMERGENCY"}
        };
        DateTimeFormatter fmt = DateTimeFormatter.ISO_LOCAL_DATE_TIME;
        for (int i = 0; i < demo.length; i++) {
            photos.add(new ClinicalPhoto(
                UUID.randomUUID(),
                patientId,
                demo[i][0],
                demo[i][1],
                demo[i][2],
                demo[i][3],
                LocalDateTime.now().minusDays(30L - (long) i * 5).format(fmt),
                demo[i][4]
            ));
        }
        return photos;
    }

    /** GET /api/clinical-photos/patient/{patientId} */
    @GetMapping("/patient/{patientId}")
    public ResponseEntity<List<ClinicalPhoto>> listByPatient(@PathVariable UUID patientId) {
        return ResponseEntity.ok(store.getOrDefault(patientId, Collections.emptyList()));
    }

    /** POST /api/clinical-photos/patient/{patientId} - multipart stub */
    @PostMapping("/patient/{patientId}")
    public ResponseEntity<ClinicalPhoto> uploadPhoto(
            @PathVariable UUID patientId,
            @RequestPart("metadata") PhotoUploadRequest request,
            @RequestPart(value = "file", required = false) MultipartFile file) {
        String url = (file != null && !file.isEmpty())
            ? "/api/clinical-photos/uploads/" + UUID.randomUUID() + "_" + file.getOriginalFilename()
            : "/api/clinical-photos/demo/placeholder.jpg";
        ClinicalPhoto photo = new ClinicalPhoto(
            UUID.randomUUID(), patientId,
            request.type(), request.tooth(), request.description(),
            url,
            LocalDateTime.now().format(DateTimeFormatter.ISO_LOCAL_DATE_TIME),
            request.category()
        );
        store.computeIfAbsent(patientId, k -> new ArrayList<>()).add(photo);
        return ResponseEntity.ok(photo);
    }

    /** DELETE /api/clinical-photos/{photoId} */
    @DeleteMapping("/{photoId}")
    public ResponseEntity<Void> deletePhoto(@PathVariable UUID photoId) {
        store.values().forEach(list -> list.removeIf(p -> p.id().equals(photoId)));
        return ResponseEntity.noContent().build();
    }

    /** GET /api/clinical-photos/patient/{patientId}/compare - before/after pairs */
    @GetMapping("/patient/{patientId}/compare")
    public ResponseEntity<List<BeforeAfterPair>> comparePhotos(@PathVariable UUID patientId) {
        List<ClinicalPhoto> photos = store.getOrDefault(patientId, Collections.emptyList());
        Map<String, ClinicalPhoto> beforeMap = photos.stream()
            .filter(p -> "BEFORE".equals(p.type()) && p.tooth() != null && !p.tooth().isBlank())
            .collect(Collectors.toMap(ClinicalPhoto::tooth, p -> p, (a, b) -> a));
        Map<String, ClinicalPhoto> afterMap = photos.stream()
            .filter(p -> "AFTER".equals(p.type()) && p.tooth() != null && !p.tooth().isBlank())
            .collect(Collectors.toMap(ClinicalPhoto::tooth, p -> p, (a, b) -> a));
        List<BeforeAfterPair> pairs = beforeMap.entrySet().stream()
            .filter(e -> afterMap.containsKey(e.getKey()))
            .map(e -> new BeforeAfterPair(
                e.getValue(), afterMap.get(e.getKey()),
                e.getKey(), "Tratamiento diente " + e.getKey()))
            .collect(Collectors.toList());
        return ResponseEntity.ok(pairs);
    }

    public record ClinicalPhoto(
        UUID id, UUID patientId,
        String type, String tooth, String description,
        String url, String takenAt, String category
    ) {}

    public record PhotoUploadRequest(
        String type, String tooth, String description, String category
    ) {}

    public record BeforeAfterPair(
        ClinicalPhoto before, ClinicalPhoto after, String tooth, String procedure
    ) {}
}
