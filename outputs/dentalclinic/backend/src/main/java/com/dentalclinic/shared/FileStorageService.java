package com.dentalclinic.shared;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.io.UncheckedIOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.UUID;

/**
 * Stores uploaded files on the local filesystem.
 * Files are saved under: <upload-dir>/<entityType>/<entityId>/<uuid>_<originalName>
 * In production replace with S3 / GCS / Azure Blob Storage.
 */
@Service
public class FileStorageService {

    private final Path uploadRoot;

    public FileStorageService(@Value("${app.upload.dir:uploads}") String uploadDir) {
        this.uploadRoot = Paths.get(uploadDir).toAbsolutePath().normalize();
        try {
            Files.createDirectories(this.uploadRoot);
        } catch (IOException e) {
            throw new UncheckedIOException("Cannot create upload directory", e);
        }
    }

    /**
     * Stores a file and returns its stored filename (UUID prefix + original name).
     */
    public String store(MultipartFile file, String entityType, String entityId) {
        if (file.isEmpty()) {
            throw new IllegalArgumentException("Cannot store empty file");
        }
        String originalName = sanitize(file.getOriginalFilename());
        String storedName = UUID.randomUUID() + "_" + originalName;
        try {
            Path dir = uploadRoot.resolve(entityType).resolve(entityId);
            Files.createDirectories(dir);
            file.transferTo(dir.resolve(storedName));
        } catch (IOException e) {
            throw new UncheckedIOException("Failed to store file " + originalName, e);
        }
        return storedName;
    }

    /**
     * Returns the absolute path for a stored file.
     */
    public Path load(String entityType, String entityId, String storedName) {
        return uploadRoot.resolve(entityType).resolve(entityId).resolve(storedName).normalize();
    }

    /**
     * Deletes a stored file. Returns true if the file existed and was deleted.
     */
    public boolean delete(String entityType, String entityId, String storedName) {
        try {
            return Files.deleteIfExists(load(entityType, entityId, storedName));
        } catch (IOException e) {
            return false;
        }
    }

    private String sanitize(String name) {
        if (name == null || name.isBlank()) return "file";
        return name.replaceAll("[^a-zA-Z0-9._\\-]", "_");
    }
}
