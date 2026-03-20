package com.dentalclinic.appointment.infrastructure.rest;

import com.dentalclinic.appointment.application.usecase.ListAllAppointmentsUseCase;
import com.dentalclinic.appointment.application.usecase.ListAllAppointmentsQuery;
import com.dentalclinic.appointment.domain.model.Appointment;
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

@Tag(name = "Appointments")
@SecurityRequirement(name = "bearerAuth")
@RestController
@RequestMapping("/appointments/export")
@CrossOrigin(origins = "*")
public class AppointmentExportController {

    private final ListAllAppointmentsUseCase listAll;
    private final ExportService exportService;

    public AppointmentExportController(ListAllAppointmentsUseCase listAll, ExportService exportService) {
        this.listAll = listAll;
        this.exportService = exportService;
    }

    @Operation(summary = "Exportar a PDF")
    @GetMapping("/pdf")
    public ResponseEntity<byte[]> exportPdf() {
        byte[] pdf = exportService.toPdf("Appointments", headers(), buildRows());
        return ResponseEntity.ok()
                .header(HttpHeaders.CONTENT_DISPOSITION, "attachment; filename=\"appointments.pdf\"")
                .contentType(MediaType.APPLICATION_PDF)
                .body(pdf);
    }

    @Operation(summary = "Exportar a Excel")
    @GetMapping("/excel")
    public ResponseEntity<byte[]> exportExcel() {
        byte[] xlsx = exportService.toExcel("Appointments", headers(), buildRows());
        return ResponseEntity.ok()
                .header(HttpHeaders.CONTENT_DISPOSITION, "attachment; filename=\"appointments.xlsx\"")
                .contentType(MediaType.parseMediaType(
                        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"))
                .body(xlsx);
    }

    private String[] headers() {
        return new String[]{"ID", "Paciente", "Dentista", "Fecha", "Estado"};
    }

    private List<String[]> buildRows() {
        return listAll.execute(new ListAllAppointmentsQuery(0, Integer.MAX_VALUE, ""))
                .content().stream()
                .map(e -> new String[]{ String.valueOf(e.getId().value()), String.valueOf(e.getPatientId()), String.valueOf(e.getDentistId()), e.getAppointmentDate() != null ? e.getAppointmentDate().toString() : "", e.getStatus() != null ? e.getStatus() != null ? e.getStatus().getValue() : "" : "" })
                .collect(Collectors.toList());
    }
}
