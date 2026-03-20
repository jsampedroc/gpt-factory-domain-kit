package com.dentalclinic.invoice.infrastructure.rest;

import com.dentalclinic.invoice.application.usecase.ListAllInvoicesUseCase;
import com.dentalclinic.invoice.application.usecase.ListAllInvoicesQuery;
import com.dentalclinic.invoice.domain.model.Invoice;
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

@Tag(name = "Invoices")
@SecurityRequirement(name = "bearerAuth")
@RestController
@RequestMapping("/invoices/export")
@CrossOrigin(origins = "*")
public class InvoiceExportController {

    private final ListAllInvoicesUseCase listAll;
    private final ExportService exportService;

    public InvoiceExportController(ListAllInvoicesUseCase listAll, ExportService exportService) {
        this.listAll = listAll;
        this.exportService = exportService;
    }

    @Operation(summary = "Exportar a PDF")
    @GetMapping("/pdf")
    public ResponseEntity<byte[]> exportPdf() {
        byte[] pdf = exportService.toPdf("Invoices", headers(), buildRows());
        return ResponseEntity.ok()
                .header(HttpHeaders.CONTENT_DISPOSITION, "attachment; filename=\"invoices.pdf\"")
                .contentType(MediaType.APPLICATION_PDF)
                .body(pdf);
    }

    @Operation(summary = "Exportar a Excel")
    @GetMapping("/excel")
    public ResponseEntity<byte[]> exportExcel() {
        byte[] xlsx = exportService.toExcel("Invoices", headers(), buildRows());
        return ResponseEntity.ok()
                .header(HttpHeaders.CONTENT_DISPOSITION, "attachment; filename=\"invoices.xlsx\"")
                .contentType(MediaType.parseMediaType(
                        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"))
                .body(xlsx);
    }

    private String[] headers() {
        return new String[]{"ID", "Paciente", "Importe", "Estado", "Fecha Emisión"};
    }

    private List<String[]> buildRows() {
        return listAll.execute(new ListAllInvoicesQuery(0, Integer.MAX_VALUE, ""))
                .content().stream()
                .map(e -> new String[]{ String.valueOf(e.getId().value()), String.valueOf(e.getPatientId()), e.getAmount() != null ? e.getAmount().toString() : "", e.getStatus() != null ? e.getStatus() != null ? e.getStatus().getValue() : "" : "", e.getIssueDate() != null ? e.getIssueDate().toString() : "" })
                .collect(Collectors.toList());
    }
}
