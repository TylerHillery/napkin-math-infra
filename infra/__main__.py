import importlib
import sys

import pulumi
import pulumi_gcp as gcp
import pulumi_github as github

from config import settings
from oidc import setup_pulumi_oidc, setup_github_oidc


if settings.STACK_NAME == "shared":
    gcp_project_config = gcp.organizations.get_project()
    gcp_project_id = gcp_project_config.number

    setup_pulumi_oidc(gcp_project_id)
    setup_github_oidc(gcp_project_id)

    benchmark_bucket = gcp.storage.Bucket(
        resource_name="benchmark-results-bucket",
        name="napkin-math-benchmark-results",
        location="US",
        uniform_bucket_level_access=True,
    )

    pulumi.export("benchmark_results_bucket_name", benchmark_bucket.name)

    github_secret_gcp_project_name = github.ActionsSecret(
        "github-actions-secret-gcp-benchmark-bucket-name",
        secret_name="GCP_BENCHMARK_BUCKET_NAME",
        repository=settings.GITHUB_REPO,
        plaintext_value=benchmark_bucket.name,
    )

    github_secret_gcp_project_name = github.ActionsSecret(
        "github-actions-secret-gcp-project-name",
        secret_name="GCP_PROJECT",
        repository=settings.GITHUB_REPO,
        plaintext_value=settings.PROJECT_NAME,
    )

    github_actions_secret_pulumi_token = github.ActionsSecret(
        "github-actions-secret-pulumi-token",
        secret_name="PULUMI_ACCESS_TOKEN",
        repository=settings.GITHUB_REPO,
        plaintext_value=settings.PULUMI_ACCESS_TOKEN,
    )



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
