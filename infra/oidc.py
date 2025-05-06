import os

import pulumi  
import pulumi_gcp as gcp
import pulumi_github as github

from config import settings
from utils import  render_template

def setup_pulumi_oidc(gcp_project_id: int):

    gcp_iam_workload_identity_pool_pulumi = gcp.iam.WorkloadIdentityPool(
        "gcp-iam-workload-identity-pool-pulumi",
        workload_identity_pool_id="pulumi-oidc",
        display_name="Pulumi OIDC",
    )

    gcp_iam_workload_identity_pool_provider_pulumi = gcp.iam.WorkloadIdentityPoolProvider(
        "gcp-iam-workload-identity-pool-provider-pulumi",
        workload_identity_pool_id=gcp_iam_workload_identity_pool_pulumi.workload_identity_pool_id,
        workload_identity_pool_provider_id="pulumi-oidc",
        attribute_mapping={
            "google.subject": "assertion.sub",
        },
        oidc=gcp.iam.WorkloadIdentityPoolProviderOidcArgs(
            issuer_uri=settings.PULUMI_OIDC_ISSUER,
            allowed_audiences=[f"gcp:{settings.ORG_NAME}"],
        ),
    )

    gcp_service_account_pulumi = gcp.serviceaccount.Account(
        "gcp-service-account-pulumi", account_id="pulumi-oidc", display_name="Pulumi OIDC"
    )

    gcp_service_account_pulumi_roles = [
        "roles/editor",
        "roles/resourcemanager.projectIamAdmin",
        "roles/iam.workloadIdentityPoolAdmin",
        "roles/iam.serviceAccountAdmin",
    ]

    for role in gcp_service_account_pulumi_roles:
        gcp.projects.IAMMember(
            f"gcp-projects-iammember-{role.split('/')[-1]}-role-pulumi",
            member=gcp_service_account_pulumi.email.apply(
                lambda email: f"serviceAccount:{email}"
            ),
            role=role,
            project=gcp_project_id,
        )

    gcp.serviceaccount.IAMBinding(
        "gcp-service-account-iam-policy-binding-pulumi",
        service_account_id=gcp_service_account_pulumi.name,
        role="roles/iam.workloadIdentityUser",
        members=gcp_iam_workload_identity_pool_pulumi.name.apply(
            lambda name: [f"principalSet://iam.googleapis.com/{name}/*"]
        ),
    )
    gcp_pulumi_esc_yml = render_template(
        templates_dir=os.path.join(os.path.dirname(__file__), "templates"),
        template_name="pulumi-esc-gcp.yml",
        gcp_project=int(gcp_project_id),
        workload_pool_id=gcp_iam_workload_identity_pool_provider_pulumi.workload_identity_pool_id,
        provider_id=gcp_iam_workload_identity_pool_provider_pulumi.workload_identity_pool_provider_id,
        service_account_email=gcp_service_account_pulumi.email,
    )

    pulumi.export("pulumi:esc-gcp", gcp_pulumi_esc_yml)

def setup_github_oidc(gcp_project_id: int):
    gcp_iam_workload_identity_pool_github_actions = gcp.iam.WorkloadIdentityPool(
        "gcp-iam-workload-identity-pool-github-actions",
        workload_identity_pool_id="github-actions-oidc",
        display_name="GitHub Actions OIDC",
    )

    gcp_iam_workload_identity_pool_provider_github_actions = gcp.iam.WorkloadIdentityPoolProvider(
        "gcp-iam-workload-identity-pool-provider-github-actions",
        workload_identity_pool_id=gcp_iam_workload_identity_pool_github_actions.workload_identity_pool_id,
        workload_identity_pool_provider_id="github-actions-oidc",
        attribute_condition=f'attribute.repository == "{settings.GITHUB_USERNAME}/{settings.PROJECT_NAME}"',
        attribute_mapping={
            "google.subject": "assertion.sub",
            "attribute.actor": "assertion.actor",
            "attribute.aud": "assertion.aud",
            "attribute.repository": "assertion.repository",
        },
        oidc=gcp.iam.WorkloadIdentityPoolProviderOidcArgs(
            issuer_uri=settings.GITHUB_OIDC_ISSUER,
        ),
    )

    gcp_service_account_github_actions = gcp.serviceaccount.Account(
        "gcp-service-account-github-actions", account_id="github-actions-service-account", display_name="github-actions"
    )

    gcp_service_account_github_actions_roles = [
        "roles/iam.serviceAccountTokenCreator",
        "roles/storage.objectViewer",
    ]

    for role in gcp_service_account_github_actions_roles:
        gcp.projects.IAMMember(
            f"gcp-projects-iammember-{role.split('/')[-1]}-role-github-actions",
            member=gcp_service_account_github_actions.email.apply(
                lambda email: f"serviceAccount:{email}"
            ),
            role=role,
            project=gcp_project_id,
        )

    workload_identity_base_path = gcp_iam_workload_identity_pool_github_actions.workload_identity_pool_id.apply(
        lambda pool_id: f"projects/{gcp_project_id}/locations/global/workloadIdentityPools/{pool_id}"
    )

    gcp.serviceaccount.IAMBinding(
        "gcp-service-account-iam-policy-binding-github-actions",
        service_account_id=gcp_service_account_github_actions.name,
        role="roles/iam.workloadIdentityUser",
        members=workload_identity_base_path.apply(
            lambda base_path: [
                f"principalSet://iam.googleapis.com/{base_path}/attribute.repository/{settings.GITHUB_USERNAME}/{settings.PROJECT_NAME}"
            ]
        ),
    )

    workload_identity_provider = workload_identity_base_path.apply(
        lambda base_path: gcp_iam_workload_identity_pool_provider_github_actions.workload_identity_pool_provider_id.apply(
            lambda provider_id: f"{base_path}/providers/{provider_id}"
        )
    )

    github.ActionsSecret(
        "github-actions-secret-github-actions-service-account-email",
        secret_name="GH_ACTIONS_SERVICE_ACCOUNT_EMAIL",
        repository=settings.GITHUB_REPO,
        plaintext_value=gcp_service_account_github_actions.email,
    )

    github.ActionsSecret(
        "github-actions-secret-workload-identity-provider",
        secret_name="WORKLOAD_IDENTITY_PROVIDER",
        repository=settings.GITHUB_REPO,
        plaintext_value=workload_identity_provider,
    )