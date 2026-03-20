package com.dentalclinic.scheduling;

import java.time.LocalDateTime;
import java.util.UUID;

public final class AppointmentEvents {
    public record AppointmentBooked(UUID appointmentId, UUID patientId, UUID clinicId,
                                     LocalDateTime startTime, String practitionerName) {}
    public record AppointmentCancelled(UUID appointmentId, UUID patientId, UUID clinicId, String reason) {}
    public record AppointmentCheckedIn(UUID appointmentId, UUID patientId, UUID clinicId) {}
    public record AppointmentCompleted(UUID appointmentId, UUID patientId, UUID clinicId) {}
    public record AppointmentRescheduled(UUID appointmentId, UUID patientId, UUID clinicId,
                                          LocalDateTime newStartTime) {}
    private AppointmentEvents() {}
}
