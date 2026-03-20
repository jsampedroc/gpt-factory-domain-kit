package com.dentalclinic.treatment.infrastructure.rest;

import com.dentalclinic.treatment.application.usecase.ListAllTreatmentsUseCase;
import com.dentalclinic.treatment.application.usecase.ListAllTreatmentsQuery;
import com.dentalclinic.treatment.domain.model.Treatment;
import com.dentalclinic.shared.ExportService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.security.SecurityRequirement;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.stream.Collectors;

@Tag(name = "Treatments")
@SecurityRequirement(name = "bearerAuth")
@RestController
@RequestMapping("/treatments/export")
@CrossOrigin(origins = "*")
public class TreatmentExportController {

    private final ListAllTreatmentsUseCase listAll;
    private final ExportService exportService;

    public TreatmentExportController(ListAllTreatmentsUseCase listAll, ExportService exportService) {
        this.listAll = listAll;
        this.exportService = exportService;
    }

    @Operation(summary = "Exportar a PDF")
    @GetMapping("/pdf")
    public ResponseEntity<byte[]> exportPdf() {
        byte[] pdf = exportService.toPdf("Treatments", headers(), buildRows());
        return ResponseEntity.ok()
                .header(HttpHeaders.CONTENT_DISPOSITION, "attachment; filename=\"treatments.pdf\"")
                .contentType(MediaType.APPLICATION_PDF)
                .body(pdf);
    }

    @Operation(summary = "Exportar a Excel")
    @GetMapping("/excel")
    public ResponseEntity<byte[]> exportExcel() {
        byte[] xlsx = exportService.toExcel("Treatments", headers(), buildRows());
        return ResponseEntity.ok()
                .header(HttpHeaders.CONTENT_DISPOSITION, "attachment; filename=\"treatments.xlsx\"")
                .contentType(MediaType.parseMediaType(
                        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"))
                .body(xlsx);
    }

    private String[] headers() {
        return new String[]{"ID", "Cita", "Descripción", "Coste"};
    }

    private List<String[]> buildRows() {
        return listAll.execute(new ListAllTreatmentsQuery(0, Integer.MAX_VALUE, ""))
                .content().stream()
                .map(e -> new String[]{ String.valueOf(e.getId().value()), String.valueOf(e.getAppointmentId()), e.getDescription(), e.getCost() != null ? e.getCost().toString() : "" })
                .collect(Collectors.toList());
    }
}
