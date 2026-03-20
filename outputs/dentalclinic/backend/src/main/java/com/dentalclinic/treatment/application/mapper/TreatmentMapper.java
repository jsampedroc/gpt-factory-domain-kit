package com.dentalclinic.treatment.application.mapper;

import com.dentalclinic.domain.valueobject.Money;
import com.dentalclinic.treatment.application.dto.TreatmentRequest;
import com.dentalclinic.treatment.application.dto.TreatmentResponse;
import com.dentalclinic.treatment.domain.model.Treatment;
import java.util.UUID;
import org.mapstruct.Mapper;

@Mapper(componentModel = "spring")
public interface TreatmentMapper {

    TreatmentResponse toResponse(Treatment entity);

}
