package com.preschoolmanagement.infrastructure.persistence.adapter;

import com.preschoolmanagement.domain.model.Classroom;
import com.preschoolmanagement.domain.repository.ClassroomRepository;
import com.preschoolmanagement.domain.valueobject.ClassroomId;
import com.preschoolmanagement.infrastructure.persistence.entity.ClassroomJpaEntity;
import com.preschoolmanagement.infrastructure.persistence.spring.SpringDataClassroomRepository;
import org.springframework.stereotype.Repository;

import java.util.Objects;
import java.util.Optional;

@Repository
public class JpaClassroomRepositoryAdapter implements ClassroomRepository {

    private final SpringDataClassroomRepository repo;

    public JpaClassroomRepositoryAdapter(SpringDataClassroomRepository repo) {
        this.repo = Objects.requireNonNull(repo);
    }

    @Override
    public Classroom save(Classroom classroom) {
        ClassroomJpaEntity entity = new ClassroomJpaEntity(
                classroom.id().value(),
                classroom.name()
        );
        ClassroomJpaEntity saved = repo.save(entity);
        return new Classroom(
                new ClassroomId(saved.getId()),
                saved.getName()
        );
    }

    @Override
    public Optional<Classroom> findById(ClassroomId id) {
        return repo.findById(id.value())
                .map(e -> new Classroom(new ClassroomId(e.getId()), e.getName()));
    }
}
