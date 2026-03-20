package com.dentalclinic.dentist.application.mapper;

import com.dentalclinic.dentist.application.dto.DentistRequest;
import com.dentalclinic.dentist.application.dto.DentistResponse;
import com.dentalclinic.dentist.domain.model.Dentist;
import java.util.UUID;
import org.mapstruct.Mapper;

@Mapper(componentModel = "spring")
public interface DentistMapper {

    DentistResponse toResponse(Dentist entity);

}
