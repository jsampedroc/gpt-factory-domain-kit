from main import SoftwareFactory, FactoryOrchestrator

def test_factory_pipeline():
    factory = SoftwareFactory("Simple order system")
    orchestrator = FactoryOrchestrator(factory)

    orchestrator.run()

    assert factory.state.domain_model is not None