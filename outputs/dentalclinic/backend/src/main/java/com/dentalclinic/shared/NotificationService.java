package com.dentalclinic.shared;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.messaging.simp.SimpMessagingTemplate;
import org.springframework.stereotype.Service;

/**
 * Sends real-time notifications to WebSocket subscribers.
 * Frontend listens on /topic/notifications.
 */
@Service
public class NotificationService {

    private static final Logger log = LoggerFactory.getLogger(NotificationService.class);
    private static final String TOPIC = "/topic/notifications";

    private final SimpMessagingTemplate messagingTemplate;

    public NotificationService(SimpMessagingTemplate messagingTemplate) {
        this.messagingTemplate = messagingTemplate;
    }

    public void send(String type, String entityType, String message) {
        NotificationMessage msg = NotificationMessage.of(type, entityType, message);
        try {
            messagingTemplate.convertAndSend(TOPIC, msg);
            log.debug("WS notification sent: {} - {}", type, message);
        } catch (Exception e) {
            log.error("Failed to send WS notification: {}", e.getMessage());
        }
    }
}
