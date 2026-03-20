package com.dentalclinic.shared;

import org.springframework.http.ResponseEntity;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDateTime;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.stream.Collectors;

@RestController
@RequestMapping("/api/backups")
@PreAuthorize("hasRole('ADMIN')")
public class BackupController {

    record BackupEntry(String id, String filename, String type, String status,
                       long sizeBytes, String s3Key, String s3Bucket,
                       String createdAt, String completedAt, String errorMessage) {}
    record BackupConfig(boolean autoBackupEnabled, String cronExpression,
                        String s3Bucket, String s3Region, String retentionDays,
                        List<String> includedDatasets) {}
    record BackupStats(int totalBackups, int successfulBackups, int failedBackups,
                       long totalSizeBytes, String lastBackupAt, String nextScheduledAt) {}

    private final Map<String, BackupEntry> backups = new ConcurrentHashMap<>();
    private BackupConfig config = new BackupConfig(
            true, "0 2 * * *", "dentalclinic-backups-prod",
            "eu-west-1", "30",
            List.of("PATIENTS", "APPOINTMENTS", "INVOICES", "CLINICAL_RECORDS", "DOCUMENTS")
    );

    public BackupController() {
        Object[][] seed = {
            {"bk1","backup_2026-03-17_02-00.zip","FULL","SUCCESS",52428800L,"backups/2026/03/backup_2026-03-17_02-00.zip","2026-03-17T02:00","2026-03-17T02:04",null},
            {"bk2","backup_2026-03-18_02-00.zip","FULL","SUCCESS",53477376L,"backups/2026/03/backup_2026-03-18_02-00.zip","2026-03-18T02:00","2026-03-18T02:04",null},
            {"bk3","backup_2026-03-19_02-00.zip","FULL","SUCCESS",54525952L,"backups/2026/03/backup_2026-03-19_02-00.zip","2026-03-19T02:00","2026-03-19T02:05",null},
            {"bk4","backup_2026-03-15_02-00.zip","FULL","FAILED",0L,"—","2026-03-15T02:00",null,"Error de conexión con S3: timeout"},
            {"bk5","backup_manual_2026-03-19_10-30.zip","MANUAL","SUCCESS",48234496L,"backups/2026/03/backup_manual_2026-03-19_10-30.zip","2026-03-19T10:30","2026-03-19T10:33",null},
        };
        for (Object[] row : seed) {
            String id = (String) row[0];
            backups.put(id, new BackupEntry(id,(String)row[1],(String)row[2],(String)row[3],
                    (long)row[4],(String)row[5],config.s3Bucket(),(String)row[6],(String)row[7],(String)row[8]));
        }
    }

    @GetMapping
    public List<BackupEntry> listAll(@RequestParam(required = false) String type) {
        return backups.values().stream()
                .filter(b -> type == null || b.type().equals(type))
                .sorted(Comparator.comparing(BackupEntry::createdAt).reversed())
                .collect(Collectors.toList());
    }

    @PostMapping("/trigger")
    public BackupEntry triggerManualBackup() {
        String id = "bk" + UUID.randomUUID().toString().substring(0, 8);
        String now = LocalDateTime.now().toString().substring(0, 16).replace("T", "_").replace(":", "-");
        String filename = "backup_manual_" + now + ".zip";
        String s3Key = "backups/" + LocalDateTime.now().getYear() + "/" +
                String.format("%02d", LocalDateTime.now().getMonthValue()) + "/" + filename;

        // Simulate backup in progress
        BackupEntry inProgress = new BackupEntry(id, filename, "MANUAL", "IN_PROGRESS",
                0L, s3Key, config.s3Bucket(),
                LocalDateTime.now().toString().substring(0, 16), null, null);
        backups.put(id, inProgress);

        // Simulate async completion (immediate for demo)
        long simulatedSize = 45 * 1024 * 1024 + (long)(Math.random() * 20 * 1024 * 1024);
        BackupEntry completed = new BackupEntry(id, filename, "MANUAL", "SUCCESS",
                simulatedSize, s3Key, config.s3Bucket(),
                inProgress.createdAt(),
                LocalDateTime.now().plusMinutes(3).toString().substring(0, 16), null);
        backups.put(id, completed);
        return completed;
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Map<String, String>> deleteBackup(@PathVariable String id) {
        if (!backups.containsKey(id)) return ResponseEntity.notFound().build();
        backups.remove(id);
        return ResponseEntity.ok(Map.of("message", "Backup eliminado de S3 y del registro."));
    }

    @GetMapping("/config")
    public BackupConfig getConfig() {
        return config;
    }

    @PutMapping("/config")
    public BackupConfig updateConfig(@RequestBody BackupConfig newConfig) {
        this.config = newConfig;
        return this.config;
    }

    @GetMapping("/stats")
    public BackupStats stats() {
        List<BackupEntry> all = new ArrayList<>(backups.values());
        long successful = all.stream().filter(b -> "SUCCESS".equals(b.status())).count();
        long failed = all.stream().filter(b -> "FAILED".equals(b.status())).count();
        long totalSize = all.stream().mapToLong(BackupEntry::sizeBytes).sum();
        String lastAt = all.stream()
                .filter(b -> "SUCCESS".equals(b.status()) && b.completedAt() != null)
                .max(Comparator.comparing(BackupEntry::completedAt))
                .map(BackupEntry::completedAt).orElse("Nunca");
        String nextAt = LocalDateTime.now().toLocalDate().plusDays(1) + "T02:00";
        return new BackupStats(all.size(), (int) successful, (int) failed, totalSize, lastAt, nextAt);
    }

    // Scheduled daily at 2am (cron: sec min hour day month weekday)
    @Scheduled(cron = "0 0 2 * * *")
    public void scheduledBackup() {
        triggerManualBackup();
    }
}
