package com.dentalclinic.shared;

import java.time.Instant;

/**
 * WebSocket notification payload sent to /topic/notifications.
 */
public record NotificationMessage(
        String type,
        String entityType,
        String message,
        Instant timestamp
) {
    public static NotificationMessage of(String type, String entityType, String message) {
        return new NotificationMessage(type, entityType, message, Instant.now());
    }
}
