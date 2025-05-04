import importlib
import sys

import pulumi
import pulumi_gcp as gcp

from config import settings
from oidc import setup_pulumi_odic


if settings.STACK_NAME == "shared":
    gcp_project_config = gcp.organizations.get_project()
    gcp_project_id = gcp_project_config.number
    setup_pulumi_odic(gcp_project_id)

    benchmark_bucket = gcp.storage.Bucket(
        resource_name="benchmark-results-bucket",
        name="napkin-math-benchmark-results",
        location="US",
        uniform_bucket_level_access=True,
    )
    pulumi.export("benchmark_results_bucket_name", benchmark_bucket.name)

else:
    module_name = f"benchmarks.{settings.STACK_NAME}"
    shared_stack = pulumi.StackReference(f"{settings.ORG_NAME}/{settings.PROJECT_NAME}/shared")
    try:
        benchmark_module = importlib.import_module(module_name)
        if hasattr(benchmark_module, "define_resources") and callable(
            benchmark_module.define_resources
        ):
            benchmark_module.define_resources(shared_stack)
        else:
            pulumi.log.error(
                f"Module '{module_name}' found, but it does not have a callable 'define_resources' function."
            )
            sys.exit(
                f"Benchmark module {module_name} is missing the 'define_resources' function."
            )

    except ModuleNotFoundError:
        pulumi.log.error(
            f"No benchmark definition module found for stack '{settings.STACK_NAME}'. Looked for '{module_name}.py'."
        )
        sys.exit(f"Benchmark module for stack '{settings.STACK_NAME}' not found.")
    except Exception as e:
        pulumi.log.error(
            f"An error occurred while running benchmark module {module_name}: {e}"
        )
        raise e
