package com.dentalclinic.config;

import org.springframework.context.annotation.Configuration;
import org.springframework.scheduling.annotation.EnableAsync;

/**
 * Enables asynchronous event listeners (e.g. email notifications).
 * Events are processed in a separate thread to avoid blocking the main request.
 */
@Configuration
@EnableAsync
public class AsyncConfig {
}
