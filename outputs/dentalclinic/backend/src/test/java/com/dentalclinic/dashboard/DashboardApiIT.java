package com.dentalclinic.dashboard;

import com.dentalclinic.AbstractIntegrationTest;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

import static org.springframework.security.test.web.servlet.request.SecurityMockMvcRequestPostProcessors.jwt;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

class DashboardApiIT extends AbstractIntegrationTest {

    @Autowired MockMvc mockMvc;

    @Test
    void getDashboard_returnsAllCounters() throws Exception {
        mockMvc.perform(get("/dashboard").with(jwt()).accept(MediaType.APPLICATION_JSON))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.totalPatients").isNumber())
                .andExpect(jsonPath("$.totalDentists").isNumber())
                .andExpect(jsonPath("$.totalAppointments").isNumber())
                .andExpect(jsonPath("$.totalTreatments").isNumber())
                .andExpect(jsonPath("$.totalInvoices").isNumber());
    }
}
