package com.dentalclinic.patient;

import com.dentalclinic.AbstractIntegrationTest;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

import static org.springframework.security.test.web.servlet.request.SecurityMockMvcRequestPostProcessors.jwt;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

class PatientApiIT extends AbstractIntegrationTest {

    @Autowired MockMvc mockMvc;

    @Test
    void getAll_returnsPageResponse() throws Exception {
        mockMvc.perform(get("/patients").with(jwt()).accept(MediaType.APPLICATION_JSON))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.content").isArray())
                .andExpect(jsonPath("$.page").value(0));
    }

    @Test
    void create_withValidData_returns200() throws Exception {
        mockMvc.perform(post("/patients")
                        .with(jwt())
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"firstName\":\"Ana\",\"lastName\":\"García\",\"birthDate\":\"1990-05-15\"}"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.firstName").value("Ana"))
                .andExpect(jsonPath("$.id").isNotEmpty());
    }

    @Test
    void create_withBlankName_returns400WithErrors() throws Exception {
        mockMvc.perform(post("/patients")
                        .with(jwt())
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"firstName\":\"\",\"lastName\":\"\",\"birthDate\":null}"))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.errors").exists());
    }

    @Test
    void getById_notFound_returns404() throws Exception {
        mockMvc.perform(get("/patients/00000000-0000-0000-0000-000000000000").with(jwt()))
                .andExpect(status().isNotFound());
    }

    @Test
    void withoutAuth_returns401() throws Exception {
        mockMvc.perform(get("/patients")).andExpect(status().isUnauthorized());
    }
}
