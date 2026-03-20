package com.dentalclinic.patient.application.mapper;

import com.dentalclinic.patient.application.dto.PatientResponse;
import com.dentalclinic.patient.domain.model.Patient;
import org.mapstruct.Mapper;
import org.mapstruct.Mapping;

@Mapper(componentModel = "spring")
public interface PatientMapper {

    @Mapping(target = "id", expression = "java(entity.getId().value())")
    @Mapping(target = "birthDate", expression = "java(entity.getBirthDate() != null ? entity.getBirthDate().toString() : null)")
    PatientResponse toResponse(Patient entity);

}
