package com.preschoolmanagement.infrastructure.persistence.adapter;

import com.preschoolmanagement.domain.model.Teacher;
import com.preschoolmanagement.domain.repository.TeacherRepository;
import com.preschoolmanagement.domain.valueobject.TeacherId;
import com.preschoolmanagement.infrastructure.persistence.entity.TeacherJpaEntity;
import com.preschoolmanagement.infrastructure.persistence.spring.SpringDataTeacherRepository;
import org.springframework.stereotype.Repository;

import java.util.Objects;
import java.util.Optional;

@Repository
public class JpaTeacherRepositoryAdapter implements TeacherRepository {

    private final SpringDataTeacherRepository repo;

    public JpaTeacherRepositoryAdapter(SpringDataTeacherRepository repo) {
        this.repo = Objects.requireNonNull(repo);
    }

    @Override
    public Teacher save(Teacher teacher) {
        TeacherJpaEntity entity = new TeacherJpaEntity(
                teacher.id().value(),
                teacher.name()
        );
        TeacherJpaEntity saved = repo.save(entity);
        return new Teacher(
                new TeacherId(saved.getId()),
                saved.getName()
        );
    }

    @Override
    public Optional<Teacher> findById(TeacherId id) {
        return repo.findById(id.value())
                .map(e -> new Teacher(new TeacherId(e.getId()), e.getName()));
    }
}
