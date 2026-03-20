package com.dentalclinic.dentist.infrastructure.rest;

import com.dentalclinic.dentist.application.usecase.ListAllDentistsUseCase;
import com.dentalclinic.dentist.application.usecase.ListAllDentistsQuery;
import com.dentalclinic.dentist.domain.model.Dentist;
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

@Tag(name = "Dentists")
@SecurityRequirement(name = "bearerAuth")
@RestController
@RequestMapping("/dentists/export")
@CrossOrigin(origins = "*")
public class DentistExportController {

    private final ListAllDentistsUseCase listAll;
    private final ExportService exportService;

    public DentistExportController(ListAllDentistsUseCase listAll, ExportService exportService) {
        this.listAll = listAll;
        this.exportService = exportService;
    }

    @Operation(summary = "Exportar a PDF")
    @GetMapping("/pdf")
    public ResponseEntity<byte[]> exportPdf() {
        byte[] pdf = exportService.toPdf("Dentists", headers(), buildRows());
        return ResponseEntity.ok()
                .header(HttpHeaders.CONTENT_DISPOSITION, "attachment; filename=\"dentists.pdf\"")
                .contentType(MediaType.APPLICATION_PDF)
                .body(pdf);
    }

    @Operation(summary = "Exportar a Excel")
    @GetMapping("/excel")
    public ResponseEntity<byte[]> exportExcel() {
        byte[] xlsx = exportService.toExcel("Dentists", headers(), buildRows());
        return ResponseEntity.ok()
                .header(HttpHeaders.CONTENT_DISPOSITION, "attachment; filename=\"dentists.xlsx\"")
                .contentType(MediaType.parseMediaType(
                        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"))
                .body(xlsx);
    }

    private String[] headers() {
        return new String[]{"ID", "Nombre", "Apellidos", "Licencia"};
    }

    private List<String[]> buildRows() {
        return listAll.execute(new ListAllDentistsQuery(0, Integer.MAX_VALUE, ""))
                .content().stream()
                .map(e -> new String[]{ String.valueOf(e.getId().value()), e.getFirstName(), e.getLastName(), e.getLicenseNumber() })
                .collect(Collectors.toList());
    }
}
