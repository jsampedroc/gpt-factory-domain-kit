package com.dentalclinic.shared;

import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.stream.Collectors;

@RestController
@RequestMapping("/api/communications")
@Tag(name = "Communications", description = "Patient messaging via email and SMS")
@PreAuthorize("hasAnyRole('ADMIN','DENTIST')")
public class CommunicationController {

    // ------------------------------------------------------------------ //
    //  In-memory message log                                               //
    // ------------------------------------------------------------------ //
    private static final Map<UUID, MessageResponse> MESSAGE_STORE = new ConcurrentHashMap<>();
    private static final Map<UUID, List<UUID>> PATIENT_INDEX      = new ConcurrentHashMap<>();

    // ------------------------------------------------------------------ //
    //  Pre-defined message templates                                       //
    // ------------------------------------------------------------------ //
    private static final List<MessageTemplate> TEMPLATES = List.of(
        new MessageTemplate("REMINDER_24H", "Recordatorio de cita",
            "EMAIL",
            "Recordatorio: su cita es mañana",
            "Estimado/a paciente, le recordamos que tiene una cita programada para mañana. " +
            "Por favor, llegue 10 minutos antes. Si necesita cancelar, contáctenos con antelación. Gracias."),
        new MessageTemplate("REMINDER_1H", "Recordatorio 1 hora",
            "SMS",
            "Cita en 1 hora",
            "Recordatorio: su cita dental es en 1 hora. Dirección: Clínica Dental, C/ Principal 1. Gracias."),
        new MessageTemplate("WELCOME", "Bienvenido a la clínica",
            "EMAIL",
            "Bienvenido/a a nuestra clínica dental",
            "Estimado/a paciente, es un placer darle la bienvenida a nuestra clínica dental. " +
            "Estamos aquí para cuidar su salud bucal con el mejor servicio. " +
            "No dude en contactarnos para cualquier consulta."),
        new MessageTemplate("BIRTHDAY", "Feliz cumpleaños",
            "EMAIL",
            "¡Feliz cumpleaños de parte de nuestra clínica!",
            "Estimado/a paciente, hoy es su día especial y queremos felicitarle. " +
            "Como regalo de cumpleaños, le ofrecemos un 10% de descuento en su próxima visita. ¡Disfrute su día!"),
        new MessageTemplate("REVIEW_REQUEST", "¿Cómo fue su visita?",
            "EMAIL",
            "Cuéntenos su experiencia en la clínica",
            "Estimado/a paciente, esperamos que su visita reciente haya sido satisfactoria. " +
            "Nos encantaría conocer su opinión para seguir mejorando. " +
            "Por favor, dedique un momento a valorar nuestra atención. ¡Gracias!"),
        new MessageTemplate("PAYMENT_REMINDER", "Recordatorio de pago pendiente",
            "EMAIL",
            "Tiene un pago pendiente en nuestra clínica",
            "Estimado/a paciente, le informamos que tiene un saldo pendiente con nuestra clínica. " +
            "Por favor, realice el pago a la mayor brevedad posible. " +
            "Si ya realizó el pago, ignore este mensaje. Gracias.")
    );

    // ------------------------------------------------------------------ //
    //  Demo seed data (8 messages)                                         //
    // ------------------------------------------------------------------ //
    static {
        String[][] seeds = {
            {"11111111-1111-1111-1111-111111111111", "Ana García",     "EMAIL", "Recordatorio: su cita es mañana",                  "SENT",      "2024-01-15T10:00:00"},
            {"11111111-1111-1111-1111-111111111111", "Ana García",     "SMS",   "Cita en 1 hora",                                   "SENT",      "2024-01-15T11:00:00"},
            {"22222222-2222-2222-2222-222222222222", "Carlos López",   "EMAIL", "Bienvenido/a a nuestra clínica dental",             "SENT",      "2024-01-10T09:00:00"},
            {"22222222-2222-2222-2222-222222222222", "Carlos López",   "EMAIL", "¡Feliz cumpleaños de parte de nuestra clínica!",    "SENT",      "2024-01-20T08:00:00"},
            {"33333333-3333-3333-3333-333333333333", "María Sánchez",  "EMAIL", "Cuéntenos su experiencia en la clínica",            "SENT",      "2024-01-18T14:00:00"},
            {"33333333-3333-3333-3333-333333333333", "María Sánchez",  "EMAIL", "Tiene un pago pendiente en nuestra clínica",        "FAILED",    "2024-01-19T09:30:00"},
            {"44444444-4444-4444-4444-444444444444", "Pedro Martín",   "SMS",   "Cita en 1 hora",                                   "SCHEDULED", "2024-02-01T10:00:00"},
            {"55555555-5555-5555-5555-555555555555", "Lucía Fernández","EMAIL", "Recordatorio: su cita es mañana",                  "PENDING",   "2024-02-05T08:00:00"},
        };
        for (String[] s : seeds) {
            UUID id  = UUID.randomUUID();
            UUID pid = UUID.fromString(s[0]);
            MessageResponse msg = new MessageResponse(
                id, pid, s[1], s[2], s[3],
                "Cuerpo del mensaje de demostración.", s[4], s[5], null
            );
            MESSAGE_STORE.put(id, msg);
            PATIENT_INDEX.computeIfAbsent(pid, k -> new ArrayList<>()).add(id);
        }
    }

    // ------------------------------------------------------------------ //
    //  POST /api/communications/send                                       //
    // ------------------------------------------------------------------ //
    @PostMapping("/send")
    @Operation(summary = "Enviar mensaje a paciente (email o SMS)")
    public ResponseEntity<MessageResponse> send(@RequestBody MessageRequest req) {
        UUID   id     = UUID.randomUUID();
        String status = (req.scheduledAt() != null && !req.scheduledAt().isBlank()) ? "SCHEDULED" : "SENT";
        String sentAt = "SENT".equals(status)
            ? LocalDateTime.now().format(DateTimeFormatter.ISO_LOCAL_DATE_TIME)
            : null;
        MessageResponse resp = new MessageResponse(
            id, req.patientId(),
            "Paciente " + req.patientId().toString().substring(0, 8),
            req.channel(), req.subject(), req.body(),
            status, sentAt, req.scheduledAt()
        );
        MESSAGE_STORE.put(id, resp);
        PATIENT_INDEX.computeIfAbsent(req.patientId(), k -> new ArrayList<>()).add(id);
        return ResponseEntity.ok(resp);
    }

    // ------------------------------------------------------------------ //
    //  GET /api/communications/patient/{patientId}                        //
    // ------------------------------------------------------------------ //
    @GetMapping("/patient/{patientId}")
    @Operation(summary = "Historial de mensajes de un paciente")
    public ResponseEntity<List<MessageResponse>> getHistory(@PathVariable UUID patientId) {
        List<UUID> ids = PATIENT_INDEX.getOrDefault(patientId, Collections.emptyList());
        List<MessageResponse> history = ids.stream()
            .map(MESSAGE_STORE::get)
            .filter(Objects::nonNull)
            .sorted(Comparator.comparing((MessageResponse m) -> m.sentAt() != null ? m.sentAt() : "").reversed())
            .collect(Collectors.toList());
        return ResponseEntity.ok(history);
    }

    // ------------------------------------------------------------------ //
    //  GET /api/communications/templates                                   //
    // ------------------------------------------------------------------ //
    @GetMapping("/templates")
    @Operation(summary = "Listar plantillas de mensajes disponibles")
    public ResponseEntity<List<MessageTemplate>> getTemplates() {
        return ResponseEntity.ok(TEMPLATES);
    }

    // ------------------------------------------------------------------ //
    //  POST /api/communications/bulk                                       //
    // ------------------------------------------------------------------ //
    @PostMapping("/bulk")
    @Operation(summary = "Envío masivo a múltiples pacientes (stub)")
    public ResponseEntity<BulkResult> bulkSend(@RequestBody BulkRequest req) {
        int          sent   = 0;
        List<String> errors = new ArrayList<>();
        String       now    = LocalDateTime.now().format(DateTimeFormatter.ISO_LOCAL_DATE_TIME);
        for (UUID pid : req.patientIds()) {
            try {
                UUID id  = UUID.randomUUID();
                MessageResponse msg = new MessageResponse(
                    id, pid, "Paciente " + pid.toString().substring(0, 8),
                    req.channel(), req.subject(), req.body(), "SENT", now, null
                );
                MESSAGE_STORE.put(id, msg);
                PATIENT_INDEX.computeIfAbsent(pid, k -> new ArrayList<>()).add(id);
                sent++;
            } catch (Exception e) {
                errors.add(pid + ": " + e.getMessage());
            }
        }
        int failed = req.patientIds().size() - sent;
        return ResponseEntity.ok(new BulkResult(req.patientIds().size(), sent, failed, errors));
    }

    // ------------------------------------------------------------------ //
    //  Records                                                             //
    // ------------------------------------------------------------------ //
    public record MessageRequest(
        UUID   patientId,
        String channel,
        String subject,
        String body,
        String scheduledAt
    ) {}

    public record MessageResponse(
        UUID   id,
        UUID   patientId,
        String patientName,
        String channel,
        String subject,
        String body,
        String status,
        String sentAt,
        String scheduledAt
    ) {}

    public record MessageTemplate(
        String code,
        String name,
        String channel,
        String subject,
        String body
    ) {}

    public record BulkRequest(
        List<UUID> patientIds,
        String     channel,
        String     subject,
        String     body
    ) {}

    public record BulkResult(
        int          total,
        int          sent,
        int          failed,
        List<String> errors
    ) {}
}
