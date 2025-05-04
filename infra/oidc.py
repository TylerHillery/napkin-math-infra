import pulumi  
import pulumi_gcp as gcp
from config import settings
from utils import  render_template

def setup_pulumi_odic(gcp_project_id: int):

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
        template_name="pulumi-esc-gcp.yml",
        gcp_project=int(gcp_project_id),
        workload_pool_id=gcp_iam_workload_identity_pool_provider_pulumi.workload_identity_pool_id,
        provider_id=gcp_iam_workload_identity_pool_provider_pulumi.workload_identity_pool_provider_id,
        service_account_email=gcp_service_account_pulumi.email,
    )

    pulumi.export("pulumi:esc-gcp", gcp_pulumi_esc_yml)