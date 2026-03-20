package com.dentalclinic.config;

import com.dentalclinic.shared.DashboardStats;
import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.security.SecurityRequirement;
import io.swagger.v3.oas.annotations.tags.Tag;
@Tag(name = "Dashboard", description = "KPIs y estadísticas del sistema")
@SecurityRequirement(name = "bearerAuth")
@RestController
@RequestMapping("/dashboard")
@CrossOrigin(origins = "*")
public class DashboardController {

    private final DashboardService service;

    public DashboardController(DashboardService service) {
        this.service = service;
    }
    @Operation(summary = "Obtener KPIs del dashboard")

    @GetMapping
    public DashboardStats getStats() {
        return service.getStats();
    }
}
