package com.preschoolmanagement.application.mapper;

import com.preschoolmanagement.application.dto.ActivityLogRequest;
import com.preschoolmanagement.application.dto.ActivityLogResponse;
import com.preschoolmanagement.domain.model.ActivityLog;
import org.mapstruct.Mapper;

@Mapper
public interface ActivityLogMapper {

    ActivityLog toDomain(ActivityLogRequest request);

    ActivityLogResponse toResponse(ActivityLog activityLog);
}
