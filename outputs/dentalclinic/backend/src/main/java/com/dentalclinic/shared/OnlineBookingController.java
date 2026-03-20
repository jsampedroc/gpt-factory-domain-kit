package com.dentalclinic.shared;

import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;

/**
 * REST controller for public patient self-service online booking.
 * Round 33 — fully public (no authentication required). In-memory store.
 */
@RestController
@RequestMapping("/api/booking")
@Tag(name = "Online Booking", description = "Public patient self-service appointment booking")
public class OnlineBookingController {

    private static final Map<String, BookingConfirmation> BOOKINGS = new ConcurrentHashMap<>();

    /** GET /api/booking/locations — list locations */
    @GetMapping("/locations")
    public ResponseEntity<List<Map<String, Object>>> listLocations() {
        List<Map<String, Object>> locs = List.of(
                Map.of("id", "10000000-0000-0000-0000-000000000001", "name", "Clínica Central",
                        "city", "Madrid", "address", "Calle Mayor 1", "active", true),
                Map.of("id", "10000000-0000-0000-0000-000000000002", "name", "Clínica Norte",
                        "city", "Barcelona", "address", "Avenida Norte 45", "active", true),
                Map.of("id", "10000000-0000-0000-0000-000000000003", "name", "Clínica Sur",
                        "city", "Sevilla", "address", "Paseo del Sur 12", "active", true)
        );
        return ResponseEntity.ok(locs);
    }

    /** GET /api/booking/locations/{locationId}/dentists — dentists at location */
    @GetMapping("/locations/{locationId}/dentists")
    public ResponseEntity<List<Map<String, Object>>> getDentists(@PathVariable String locationId) {
        List<Map<String, Object>> dentists = List.of(
                Map.of("id", "20000000-0000-0000-0000-000000000001", "name", "Dr. García", "specialty", "Ortodoncista"),
                Map.of("id", "20000000-0000-0000-0000-000000000002", "name", "Dra. López", "specialty", "Endodoncista"),
                Map.of("id", "20000000-0000-0000-0000-000000000003", "name", "Dr. Martínez", "specialty", "Cirujano oral")
        );
        return ResponseEntity.ok(dentists);
    }

    /** GET /api/booking/locations/{locationId}/availability?date=YYYY-MM-DD&dentistId=xxx — slots */
    @GetMapping("/locations/{locationId}/availability")
    public ResponseEntity<List<Map<String, Object>>> getAvailability(
            @PathVariable String locationId,
            @RequestParam(required = false) String date,
            @RequestParam(required = false) String dentistId) {
        String[] times = {"09:00","10:00","11:00","12:00","13:00","14:00","15:00","16:00"};
        boolean[] avail = {true, true, false, true, true, false, true, true};
        List<Map<String, Object>> slots = new ArrayList<>();
        for (int i = 0; i < times.length; i++) {
            slots.add(Map.of("time", times[i], "available", avail[i]));
        }
        return ResponseEntity.ok(slots);
    }

    /** POST /api/booking/request — patient submits booking request */
    @PostMapping("/request")
    public ResponseEntity<BookingConfirmation> requestBooking(@RequestBody BookingRequest req) {
        String confirmCode = "BOOK-" + UUID.randomUUID().toString().substring(0, 8).toUpperCase();
        String locationName = resolveLocationName(req.locationId());
        String dentistName = resolveDentistName(req.dentistId());
        BookingConfirmation confirmation = new BookingConfirmation(
                confirmCode,
                req.patientName(),
                req.date(),
                req.time(),
                locationName,
                dentistName,
                req.procedure() != null ? req.procedure() : "Consulta general",
                "PENDING"
        );
        BOOKINGS.put(confirmCode, confirmation);
        return ResponseEntity.ok(confirmation);
    }

    /** GET /api/booking/confirm/{confirmCode} — confirm booking (returns booking details) */
    @GetMapping("/confirm/{confirmCode}")
    public ResponseEntity<BookingConfirmation> confirmBooking(@PathVariable String confirmCode) {
        BookingConfirmation booking = BOOKINGS.get(confirmCode);
        if (booking == null) {
            return ResponseEntity.notFound().build();
        }
        if ("PENDING".equals(booking.status())) {
            BookingConfirmation confirmed = new BookingConfirmation(
                    booking.confirmCode(), booking.patientName(), booking.date(), booking.time(),
                    booking.locationName(), booking.dentistName(), booking.procedure(), "CONFIRMED"
            );
            BOOKINGS.put(confirmCode, confirmed);
            return ResponseEntity.ok(confirmed);
        }
        return ResponseEntity.ok(booking);
    }

    private String resolveLocationName(UUID locationId) {
        if (locationId == null) return "Clínica Central";
        String sid = locationId.toString();
        if (sid.endsWith("0001")) return "Clínica Central";
        if (sid.endsWith("0002")) return "Clínica Norte";
        if (sid.endsWith("0003")) return "Clínica Sur";
        return "Clínica Central";
    }

    private String resolveDentistName(UUID dentistId) {
        if (dentistId == null) return "Dr. García";
        String sid = dentistId.toString();
        if (sid.endsWith("0001")) return "Dr. García";
        if (sid.endsWith("0002")) return "Dra. López";
        if (sid.endsWith("0003")) return "Dr. Martínez";
        return "Dr. García";
    }

    // ---------------------------------------------------------------
    // Records
    // ---------------------------------------------------------------

    public record BookingRequest(
            String patientName,
            String patientPhone,
            String patientEmail,
            UUID locationId,
            UUID dentistId,
            String date,
            String time,
            String procedure,
            String notes
    ) {}

    public record BookingConfirmation(
            String confirmCode,
            String patientName,
            String date,
            String time,
            String locationName,
            String dentistName,
            String procedure,
            String status
    ) {}
}
