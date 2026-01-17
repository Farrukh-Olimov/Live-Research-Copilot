import pytest

from common.datasources.registry.schema_registry import DatasourceSchemaRegistry


def test_registry_is_empty_after_reset(reset_datasource_registry):
    """Tests that the datasource registry is empty.

    This test ensures that the datasource registry is
    cleared before and after each test.
    """
    assert (
        not DatasourceSchemaRegistry.list_schemas()
    ), "Datasource registry should be empty."


def test_register_datasource_schema(reset_datasource_registry):
    """Tests that a datasource schema can be registered.

    This test ensures that a datasource schema can be
    registered in the datasource registry.
    """
    from common.datasources.schema import BasePaperSchema

    class TestSchema(BasePaperSchema):
        DATASOURCE_NAME = "test_schema"

    DatasourceSchemaRegistry.register(TestSchema)
    assert (
        DatasourceSchemaRegistry.list_schemas()
    ), "Datasource registry should not be empty."

    schema = DatasourceSchemaRegistry.get_schema(TestSchema.DATASOURCE_NAME)
    assert (
        schema.DATASOURCE_NAME == TestSchema.DATASOURCE_NAME
    ), "Schema should be registered."

    DatasourceSchemaRegistry.register(TestSchema)


def test_register_datasource_schema_in_parallel(reset_datasource_registry):
    """Tests that a datasource schema can be registered in parallel.

    This test ensures that a datasource schema can be registered
    in parallel without any issues.
    """
    from threading import Thread

    from common.datasources.schema import BasePaperSchema

    class TestSchema(BasePaperSchema):
        DATASOURCE_NAME = "test_schema"

    class TestSchema2(BasePaperSchema):
        DATASOURCE_NAME = "test_schema2"

    def register(i: int):
        DatasourceSchemaRegistry.register(TestSchema if i % 2 == 0 else TestSchema2)

    threads = [Thread(target=register, args=(i,)) for i in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    schemas = DatasourceSchemaRegistry.list_schemas()
    assert len(schemas) == 2, "Only one schema should be registered"


def test_get_unregistered_datasource_schema(reset_datasource_registry):
    """Tests that returns all registered datasource schemas.

    This test ensures that the datasource registry is populated with all
    available datasource schemas.
    """
    from common.datasources.schema import BasePaperSchema

    class TestSchema(BasePaperSchema):
        DATASOURCE_NAME = "test_schema"

    DatasourceSchemaRegistry.register(TestSchema)
    assert (
        DatasourceSchemaRegistry.list_schemas()
    ), "Datasource registry should not be empty."

    schema = DatasourceSchemaRegistry.get_schema(TestSchema.DATASOURCE_NAME)
    assert (
        schema.DATASOURCE_NAME == TestSchema.DATASOURCE_NAME
    ), "Schema should be registered."

    DatasourceSchemaRegistry.unregister(TestSchema.DATASOURCE_NAME)

    # Expect KeyError because the schema has been unregistered
    with pytest.raises(KeyError):
        DatasourceSchemaRegistry.get_schema(TestSchema.DATASOURCE_NAME)

    # Expect KeyError because the schema has been unregistered
    with pytest.raises(KeyError):
        DatasourceSchemaRegistry.unregister(TestSchema.DATASOURCE_NAME)


# def test_auto_import_registers_all_datasource_schemas():
#     """Tests that imports all datasource schemas.

#     This test ensures that the datasource registry is populated with all
#     available datasource schemas.
#     """
#     from common.datasources import auto_import_datasource_schemas

#     auto_import_datasource_schemas()
#     assert (
#         DatasourceSchemaRegistry.list_schemas()
#     ), "Datasource registry should not be empty."


# def test_get_registered_datasource_schemas():
#     """Tests that returns all registered datasource schemas.

#     This test ensures that the datasource registry is populated with all
#     available datasource schemas.
#     """
#     from common.datasources import auto_import_datasource_schemas

#     auto_import_datasource_schemas()

#     registered_schemas = DatasourceSchemaRegistry.list_schemas()
#     print(f"Registered schemas: {registered_schemas}")
#     assert registered_schemas, "Datasource registry should not be empty."

#     schema_name = registered_schemas[0]
#     schema = DatasourceSchemaRegistry.get_schema(schema_name)

#     assert (
#         schema.DATASOURCE_NAME == schema_name
#     ), f"Schema {schema_name} should be registered."
