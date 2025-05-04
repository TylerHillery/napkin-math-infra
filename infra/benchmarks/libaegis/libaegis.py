import pulumi
import pulumi_gcp as gcp

from config import settings
from utils import render_template
import os


def define_resources(shared_stack: pulumi.StackReference):
    startup_script = render_template(
        templates_dir=os.path.join(os.path.dirname(__file__), "templates"),
        template_name="startup.sh",
        bucket_name=shared_stack.get_output("benchmark_results_bucket_name"),
        benchmark_name=settings.STACK_NAME,
    )

    pulumi.export(f"{settings.STACK_NAME}:startup-script", startup_script)

    vm = gcp.compute.Instance(
        f"{settings.STACK_NAME}-vm",
        machine_type="e2-micro",
        zone="us-central1-a",
        boot_disk=gcp.compute.InstanceBootDiskArgs(
            initialize_params=gcp.compute.InstanceBootDiskInitializeParamsArgs(
                image="debian-cloud/debian-12",
            ),
        ),
        network_interfaces=[
            gcp.compute.InstanceNetworkInterfaceArgs(
                network="default",
                access_configs=[gcp.compute.InstanceNetworkInterfaceAccessConfigArgs()],
            )
        ],
        service_account=gcp.compute.InstanceServiceAccountArgs(
            scopes=["https://www.googleapis.com/auth/cloud-platform"],
        ),
        metadata_startup_script=startup_script,
        tags=[settings.STACK_NAME, "benchmark-vm"],
        deletion_protection=False,
        allow_stopping_for_update=True,
    )

    pulumi.export(f"{settings.STACK_NAME}_vm_name", vm.name)
