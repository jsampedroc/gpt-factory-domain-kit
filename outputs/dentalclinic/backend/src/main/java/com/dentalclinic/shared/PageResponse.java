package com.dentalclinic.shared;

import java.util.List;

public record PageResponse<T>(
        List<T> content,
        int page,
        int size,
        long total,
        int totalPages,
        boolean last) {}
