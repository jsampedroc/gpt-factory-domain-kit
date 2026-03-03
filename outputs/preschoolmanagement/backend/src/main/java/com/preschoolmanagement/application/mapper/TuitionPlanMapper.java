package com.preschoolmanagement.application.mapper;

import com.preschoolmanagement.application.dto.TuitionPlanRequest;
import com.preschoolmanagement.application.dto.TuitionPlanResponse;
import com.preschoolmanagement.domain.model.TuitionPlan;
import org.mapstruct.Mapper;

@Mapper
public interface TuitionPlanMapper {

    TuitionPlan toDomain(TuitionPlanRequest request);

    TuitionPlanResponse toResponse(TuitionPlan tuitionPlan);
}
