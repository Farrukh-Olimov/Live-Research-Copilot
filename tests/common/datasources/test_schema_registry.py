import pytest

from common.datasources.schema_registry import DatasourceSchemas


def test_registry_is_empty_after_reset(reset_datasource_registry):
    """Tests that the datasource registry is empty.

    This test ensures that the datasource registry is
    cleared before and after each test.
    """
    assert not DatasourceSchemas.list_schemas(), "Datasource registry should be empty."


def test_register_datasource_schema(reset_datasource_registry):
    """Tests that a datasource schema can be registered.

    This test ensures that a datasource schema can be
    registered in the datasource registry.
    """
    from common.datasources.schema import BasePaperSchema

    class TestSchema(BasePaperSchema):
        source_name = "test_schema"

    DatasourceSchemas.register(TestSchema)
    assert DatasourceSchemas.list_schemas(), "Datasource registry should not be empty."

    schema = DatasourceSchemas.get_schema(TestSchema.source_name)
    assert schema.source_name == TestSchema.source_name, "Schema should be registered."

    DatasourceSchemas.register(TestSchema)


def test_register_datasource_schema_in_parallel(reset_datasource_registry):
    """Tests that a datasource schema can be registered in parallel.

    This test ensures that a datasource schema can be registered
    in parallel without any issues.
    """
    from threading import Thread

    from common.datasources.schema import BasePaperSchema

    class TestSchema(BasePaperSchema):
        source_name = "test_schema"

    class TestSchema2(BasePaperSchema):
        source_name = "test_schema2"

    def register(i: int):
        DatasourceSchemas.register(TestSchema if i % 2 == 0 else TestSchema2)

    threads = [Thread(target=register, args=(i,)) for i in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    schemas = DatasourceSchemas.list_schemas()
    assert len(schemas) == 2, "Only one schema should be registered"


def test_get_unregistered_datasource_schema(reset_datasource_registry):
    """Tests that returns all registered datasource schemas.

    This test ensures that the datasource registry is populated with all
    available datasource schemas.
    """
    from common.datasources.schema import BasePaperSchema

    class TestSchema(BasePaperSchema):
        source_name = "test_schema"

    DatasourceSchemas.register(TestSchema)
    assert DatasourceSchemas.list_schemas(), "Datasource registry should not be empty."

    schema = DatasourceSchemas.get_schema(TestSchema.source_name)
    assert schema.source_name == TestSchema.source_name, "Schema should be registered."

    DatasourceSchemas.unregister(TestSchema.source_name)

    # Expect KeyError because the schema has been unregistered
    with pytest.raises(KeyError):
        DatasourceSchemas.get_schema(TestSchema.source_name)

    # Expect KeyError because the schema has been unregistered
    with pytest.raises(KeyError):
        DatasourceSchemas.unregister(TestSchema.source_name)


def test_auto_import_registers_all_datasource_schemas():
    """Tests that imports all datasource schemas.

    This test ensures that the datasource registry is populated with all
    available datasource schemas.
    """
    from common.datasources import auto_import_datasource_schemas

    auto_import_datasource_schemas()
    assert DatasourceSchemas.list_schemas(), "Datasource registry should not be empty."


def test_get_registered_datasource_schemas():
    """Tests that returns all registered datasource schemas.

    This test ensures that the datasource registry is populated with all
    available datasource schemas.
    """
    from common.datasources import auto_import_datasource_schemas

    auto_import_datasource_schemas()

    registered_schemas = DatasourceSchemas.list_schemas()
    print(f"Registered schemas: {registered_schemas}")
    assert registered_schemas, "Datasource registry should not be empty."

    schema_name = registered_schemas[0]
    schema = DatasourceSchemas.get_schema(schema_name)

    assert (
        schema.source_name == schema_name
    ), f"Schema {schema_name} should be registered."
