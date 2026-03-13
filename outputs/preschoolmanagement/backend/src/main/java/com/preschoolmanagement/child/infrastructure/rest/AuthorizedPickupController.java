package com.preschoolmanagement.child.infrastructure.rest;

import com.preschoolmanagement.child.application.usecase.AuthorizedPickupUseCase;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/authorizedpickups")
public class AuthorizedPickupController {

    private final AuthorizedPickupUseCase useCase;

    public AuthorizedPickupController(AuthorizedPickupUseCase useCase) {
        this.useCase = useCase;
    }

}
