package com.dentalclinic.config;

import com.github.benmanes.caffeine.cache.Caffeine;
import org.springframework.cache.CacheManager;
import org.springframework.cache.annotation.EnableCaching;
import org.springframework.cache.caffeine.CaffeineCacheManager;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import java.util.concurrent.TimeUnit;

/**
 * Caffeine cache configuration.
 * Caches frequently-read, infrequently-changed data (entities by ID, dashboard stats).
 * TTL: 5 minutes. Max size: 500 entries per cache.
 */
@Configuration
@EnableCaching
public class CacheConfig {

    public static final String CACHE_ENTITY_BY_ID = "entityById";
    public static final String CACHE_DASHBOARD     = "dashboard";

    @Bean
    public CacheManager cacheManager() {
        CaffeineCacheManager manager = new CaffeineCacheManager(
                CACHE_ENTITY_BY_ID,
                CACHE_DASHBOARD
        );
        manager.setCaffeine(
                Caffeine.newBuilder()
                        .maximumSize(500)
                        .expireAfterWrite(5, TimeUnit.MINUTES)
                        .recordStats()
        );
        return manager;
    }
}
