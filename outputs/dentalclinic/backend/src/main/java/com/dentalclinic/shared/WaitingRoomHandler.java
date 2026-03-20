package com.dentalclinic.shared;

import org.springframework.messaging.handler.annotation.MessageMapping;
import org.springframework.messaging.handler.annotation.SendTo;
import org.springframework.stereotype.Controller;

/**
 * WebSocket message handler for the waiting room feature.
 * Frontend publishes to /app/waiting-room, server broadcasts to /topic/waiting-room.
 */
@Controller
public class WaitingRoomHandler {

    /**
     * Relay waiting room events (ADD, UPDATE, REMOVE) to all subscribers.
     * In production, persist queue state to DB for recovery on restart.
     */
    @MessageMapping("/waiting-room")
    @SendTo("/topic/waiting-room")
    public Object relay(Object event) {
        return event;  // relay as-is; enrich here if needed
    }
}
