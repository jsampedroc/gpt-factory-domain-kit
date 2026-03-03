# ai/tasks/write_tests_task.py


def build_write_tests_task(path, base_package, context_data="", **kwargs):
    return {
        "agent": "backend_builder",
        "description": f"""
        Generate a professional unit test battery (JUnit 5 + Mockito + AssertJ) for '{path}'.
        
        SOURCE CODE CONTEXT:
        {context_data}

        STRICT TESTING RULES:
        1. INSTANTIATION: Entities have PROTECTED constructors. Use ONLY '[Class].create(...)' or factory methods.
        2. IDENTITIES: Do not mock IDs. Instantiate them: 'new IdName(UUID.randomUUID())'.
        3. MOCKING: Use @ExtendWith(MockitoExtension.class) and @Mock for dependencies.
        4. ASSERTIONS: Use AssertJ 'assertThat(...)'.
        5. PACKAGE: Root package is '{base_package}'. File must be in the mirror 'src/test/java/' path.
        """,
        "expected_output": "Compilable, high-coverage JUnit 5 code."
    }