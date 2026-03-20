package com.dentalclinic.config;

import com.dentalclinic.patient.domain.event.PatientRegisteredEvent;
import com.dentalclinic.dentist.domain.event.DentistRegisteredEvent;
import com.dentalclinic.appointment.domain.event.AppointmentScheduledEvent;
import com.dentalclinic.appointment.domain.event.AppointmentCancelledEvent;
import com.dentalclinic.invoice.domain.event.InvoiceCreatedEvent;
import com.dentalclinic.shared.NotificationService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.event.EventListener;
import org.springframework.mail.SimpleMailMessage;
import org.springframework.mail.javamail.JavaMailSender;
import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Component;

/**
 * Listens to domain events and sends email notifications.
 * Uses MailHog in development (see application.properties).
 */
@Component
public class NotificationEventListener {

    private static final Logger log = LoggerFactory.getLogger(NotificationEventListener.class);

    private final JavaMailSender mailSender;
    private final NotificationService notificationService;

    @Value("${app.notifications.from:noreply@dentalclinic.com}")
    private String from;

    @Value("${app.notifications.admin:admin@dentalclinic.com}")
    private String adminEmail;

    @Value("${app.notifications.enabled:true}")
    private boolean enabled;

    public NotificationEventListener(JavaMailSender mailSender, NotificationService notificationService) {
        this.mailSender = mailSender;
        this.notificationService = notificationService;
    }

    @Async
    @EventListener
    public void onPatientRegistered(PatientRegisteredEvent event) {
        notificationService.send("CREATED", "Patient", "Nuevo paciente: " + event.firstName() + " " + event.lastName());
        log.info("[EVENT] {} - Patient registered: {} {} (id={})",
                event.eventType(), event.firstName(), event.lastName(), event.patientId());
        if (!enabled) return;
        sendEmail(adminEmail,
                "Nuevo paciente registrado",
                "Se ha registrado un nuevo paciente:\n\n" +
                "Nombre: " + event.firstName() + " " + event.lastName() + "\n" +
                "ID: " + event.patientId());
    }

    @Async
    @EventListener
    public void onDentistRegistered(DentistRegisteredEvent event) {
        notificationService.send("CREATED", "Dentist", "Nuevo dentista: " + event.firstName() + " " + event.lastName());
        log.info("[EVENT] {} - Dentist registered: {} {} license={} (id={})",
                event.eventType(), event.firstName(), event.lastName(),
                event.licenseNumber(), event.dentistId());
        if (!enabled) return;
        sendEmail(adminEmail,
                "Nuevo dentista registrado",
                "Se ha registrado un nuevo dentista:\n\n" +
                "Nombre: " + event.firstName() + " " + event.lastName() + "\n" +
                "Licencia: " + event.licenseNumber() + "\n" +
                "ID: " + event.dentistId());
    }

    @Async
    @EventListener
    public void onAppointmentScheduled(AppointmentScheduledEvent event) {
        notificationService.send("CREATED", "Appointment", "Nueva cita: " + event.appointmentDate());
        log.info("[EVENT] {} - Appointment scheduled: id={} date={}",
                event.eventType(), event.appointmentId(), event.appointmentDate());
        if (!enabled) return;
        sendEmail(adminEmail,
                "Nueva cita programada",
                "Se ha programado una nueva cita:\n\n" +
                "Fecha: " + event.appointmentDate() + "\n" +
                "Paciente ID: " + event.patientId() + "\n" +
                "Dentista ID: " + event.dentistId() + "\n" +
                "Cita ID: " + event.appointmentId());
    }

    @Async
    @EventListener
    public void onAppointmentCancelled(AppointmentCancelledEvent event) {
        notificationService.send("DELETED", "Appointment", "Cita cancelada: " + event.appointmentId());
        log.info("[EVENT] {} - Appointment cancelled: id={}", event.eventType(), event.appointmentId());
        if (!enabled) return;
        sendEmail(adminEmail,
                "Cita cancelada",
                "Se ha cancelado la cita con ID: " + event.appointmentId());
    }

    @Async
    @EventListener
    public void onInvoiceCreated(InvoiceCreatedEvent event) {
        notificationService.send("CREATED", "Invoice", "Nueva factura para paciente: " + event.patientId());
        log.info("[EVENT] {} - Invoice created: id={} patient={}",
                event.eventType(), event.invoiceId(), event.patientId());
        if (!enabled) return;
        sendEmail(adminEmail,
                "Nueva factura creada",
                "Se ha creado una nueva factura:\n\n" +
                "Factura ID: " + event.invoiceId() + "\n" +
                "Paciente ID: " + event.patientId());
    }

    private void sendEmail(String to, String subject, String body) {
        try {
            SimpleMailMessage msg = new SimpleMailMessage();
            msg.setFrom(from);
            msg.setTo(to);
            msg.setSubject(subject);
            msg.setText(body);
            mailSender.send(msg);
            log.debug("Email sent to {} - Subject: {}", to, subject);
        } catch (Exception e) {
            log.error("Failed to send email to {}: {}", to, e.getMessage());
        }
    }
}
