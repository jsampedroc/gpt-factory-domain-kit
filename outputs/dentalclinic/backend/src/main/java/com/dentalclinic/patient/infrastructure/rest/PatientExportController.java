package com.dentalclinic.patient.infrastructure.rest;

import com.dentalclinic.patient.application.usecase.ListAllPatientsUseCase;
import com.dentalclinic.patient.application.usecase.ListAllPatientsQuery;
import com.dentalclinic.patient.domain.model.Patient;
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

@Tag(name = "Patients")
@SecurityRequirement(name = "bearerAuth")
@RestController
@RequestMapping("/patients/export")
@CrossOrigin(origins = "*")
public class PatientExportController {

    private final ListAllPatientsUseCase listAll;
    private final ExportService exportService;

    public PatientExportController(ListAllPatientsUseCase listAll, ExportService exportService) {
        this.listAll = listAll;
        this.exportService = exportService;
    }

    @Operation(summary = "Exportar a PDF")
    @GetMapping("/pdf")
    public ResponseEntity<byte[]> exportPdf() {
        byte[] pdf = exportService.toPdf("Patients", headers(), buildRows());
        return ResponseEntity.ok()
                .header(HttpHeaders.CONTENT_DISPOSITION, "attachment; filename=\"patients.pdf\"")
                .contentType(MediaType.APPLICATION_PDF)
                .body(pdf);
    }

    @Operation(summary = "Exportar a Excel")
    @GetMapping("/excel")
    public ResponseEntity<byte[]> exportExcel() {
        byte[] xlsx = exportService.toExcel("Patients", headers(), buildRows());
        return ResponseEntity.ok()
                .header(HttpHeaders.CONTENT_DISPOSITION, "attachment; filename=\"patients.xlsx\"")
                .contentType(MediaType.parseMediaType(
                        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"))
                .body(xlsx);
    }

    private String[] headers() {
        return new String[]{"ID", "Nombre", "Apellidos", "Fecha Nacimiento"};
    }

    private List<String[]> buildRows() {
        return listAll.execute(new ListAllPatientsQuery(0, Integer.MAX_VALUE, ""))
                .content().stream()
                .map(e -> new String[]{ String.valueOf(e.getId().value()), e.getFirstName(), e.getLastName(), e.getBirthDate() != null ? e.getBirthDate().toString() : "" })
                .collect(Collectors.toList());
    }
}
