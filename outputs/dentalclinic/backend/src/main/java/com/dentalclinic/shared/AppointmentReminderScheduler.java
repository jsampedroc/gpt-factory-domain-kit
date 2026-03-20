package com.dentalclinic.shared;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.mail.SimpleMailMessage;
import org.springframework.mail.javamail.JavaMailSender;
import org.springframework.scheduling.annotation.EnableScheduling;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;

/**
 * Sends appointment reminder emails 24 hours before the scheduled time.
 * Runs every hour via @Scheduled(cron).
 * In production, track sent reminders in DB to avoid duplicates.
 */
@Service
@EnableScheduling
public class AppointmentReminderScheduler {

    private static final Logger log = LoggerFactory.getLogger(AppointmentReminderScheduler.class);
    private static final DateTimeFormatter FMT = DateTimeFormatter.ofPattern("dd/MM/yyyy HH:mm");

    private final JavaMailSender mailSender;

    public AppointmentReminderScheduler(JavaMailSender mailSender) {
        this.mailSender = mailSender;
    }

    /**
     * Runs every hour. Override in subclass or via bean to inject real appointment data.
     * This is the base implementation — wire with your AppointmentRepository.
     */
    @Scheduled(cron = "0 0 * * * *")
    public void sendReminders() {
        log.info("[Scheduler] Checking appointments for 24h reminders at {}", LocalDateTime.now().format(FMT));
        // TODO: inject AppointmentRepository and query appointments in next 24h
        // List<Appointment> upcoming = appointmentRepo.findByDateBetween(now, now.plusHours(24));
        // upcoming.stream().filter(a -> !a.reminderSent()).forEach(this::sendReminder);
    }

    protected void sendReminder(String patientEmail, String patientName,
                                 String dentistName, LocalDateTime appointmentDate) {
        try {
            SimpleMailMessage msg = new SimpleMailMessage();
            msg.setTo(patientEmail);
            msg.setSubject("Recordatorio de cita dental");
            msg.setText(String.format(
                "Hola %s,\n\nLe recordamos que tiene una cita con el/la Dr/a. %s " +
                "el día %s.\n\nSi necesita cancelar o modificar la cita, contacte con nosotros " +
                "con antelación.\n\nUn saludo,\nClínica Dental",
                patientName, dentistName, appointmentDate.format(FMT)
            ));
            mailSender.send(msg);
            log.info("[Scheduler] Reminder sent to {}", patientEmail);
        } catch (Exception e) {
            log.error("[Scheduler] Failed to send reminder to {}: {}", patientEmail, e.getMessage());
        }
    }
}
