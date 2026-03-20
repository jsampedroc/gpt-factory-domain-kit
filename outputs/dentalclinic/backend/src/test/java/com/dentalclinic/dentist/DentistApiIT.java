package com.dentalclinic.dentist;

import com.dentalclinic.AbstractIntegrationTest;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

import static org.springframework.security.test.web.servlet.request.SecurityMockMvcRequestPostProcessors.jwt;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

class DentistApiIT extends AbstractIntegrationTest {

    @Autowired MockMvc mockMvc;

    @Test
    void getAll_returnsPageResponse() throws Exception {
        mockMvc.perform(get("/dentists").with(jwt()).accept(MediaType.APPLICATION_JSON))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.content").isArray());
    }

    @Test
    void create_withValidData_returns200() throws Exception {
        mockMvc.perform(post("/dentists")
                        .with(jwt())
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"firstName\":\"Carlos\",\"lastName\":\"Martínez\",\"licenseNumber\":\"LIC-12345\"}"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.licenseNumber").value("LIC-12345"));
    }

    @Test
    void create_withBlankLicense_returns400() throws Exception {
        mockMvc.perform(post("/dentists")
                        .with(jwt())
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"firstName\":\"Test\",\"lastName\":\"Test\",\"licenseNumber\":\"\"}"))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.errors.licenseNumber").exists());
    }
}
