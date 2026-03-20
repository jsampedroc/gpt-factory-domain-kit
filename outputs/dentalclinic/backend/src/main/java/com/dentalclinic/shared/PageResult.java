package com.dentalclinic.shared;

import java.util.List;

public record PageResult<T>(
        List<T> content,
        int page,
        int size,
        long total) {

    public int totalPages() {
        return size == 0 ? 0 : (int) Math.ceil((double) total / size);
    }

    public boolean isLast() {
        return page >= totalPages() - 1;
    }
}
