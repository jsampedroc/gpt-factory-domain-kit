package com.dentalclinic.shared;

import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.security.oauth2.jwt.Jwt;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.time.Instant;
import java.util.*;

/**
 * Handles file uploads and downloads for any domain entity.
 * Files are stored on disk by FileStorageService.
 * Metadata is kept in memory (replace with DB persistence for production).
 */
@RestController
@RequestMapping("/api/documents")
public class DocumentController {

    private final FileStorageService storageService;
    // In-memory store: entityType+entityId -> list of metadata
    // Replace with a JPA repository backed by the documents table in production.
    private final Map<String, List<DocumentMeta>> store = new java.util.concurrent.ConcurrentHashMap<>();

    public DocumentController(FileStorageService storageService) {
        this.storageService = storageService;
    }

    @PostMapping(value = "/{entityType}/{entityId}",
                 consumes = MediaType.MULTIPART_FORM_DATA_VALUE)
    public ResponseEntity<DocumentMeta> upload(
            @PathVariable String entityType,
            @PathVariable String entityId,
            @RequestParam("file") MultipartFile file,
            @AuthenticationPrincipal Jwt jwt) {

        String uploader = jwt != null ? jwt.getSubject() : "anonymous";
        String storedName = storageService.store(file, entityType, entityId);
        DocumentMeta meta = new DocumentMeta(
                UUID.randomUUID().toString(), entityType, entityId,
                file.getOriginalFilename(), storedName,
                file.getContentType(), file.getSize(),
                uploader, Instant.now());
        store.computeIfAbsent(entityType + ":" + entityId, k -> new ArrayList<>()).add(meta);
        return ResponseEntity.ok(meta);
    }

    @GetMapping("/{entityType}/{entityId}")
    public ResponseEntity<List<DocumentMeta>> list(
            @PathVariable String entityType,
            @PathVariable String entityId) {
        return ResponseEntity.ok(store.getOrDefault(entityType + ":" + entityId, List.of()));
    }

    @DeleteMapping("/{entityType}/{entityId}/{storedName}")
    public ResponseEntity<Void> delete(
            @PathVariable String entityType,
            @PathVariable String entityId,
            @PathVariable String storedName) {
        storageService.delete(entityType, entityId, storedName);
        List<DocumentMeta> docs = store.get(entityType + ":" + entityId);
        if (docs != null) docs.removeIf(d -> d.storedName().equals(storedName));
        return ResponseEntity.noContent().build();
    }

    public record DocumentMeta(
            String id,
            String entityType,
            String entityId,
            String originalName,
            String storedName,
            String contentType,
            long fileSize,
            String uploadedBy,
            Instant uploadedAt) {}
}
