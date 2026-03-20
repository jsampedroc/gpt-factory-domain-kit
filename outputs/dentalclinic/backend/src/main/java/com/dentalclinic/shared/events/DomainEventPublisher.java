package com.dentalclinic.shared.events;

import org.springframework.context.ApplicationEventPublisher;
import org.springframework.stereotype.Component;

@Component
public class DomainEventPublisher {
    private final ApplicationEventPublisher publisher;
    public DomainEventPublisher(ApplicationEventPublisher publisher) {
        this.publisher = publisher;
    }
    public void publish(Object event) {
        publisher.publishEvent(event);
    }
}
