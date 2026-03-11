package com.preschoolmanagement.child.infrastructure.rest;

import com.preschoolmanagement.child.application.service.AuthorizedPickupService;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/authorizedpickups")
public class AuthorizedPickupController {

    private final AuthorizedPickupService service;

    public AuthorizedPickupController(AuthorizedPickupService service) {
        this.service = service;
    }

}
