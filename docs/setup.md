## Steps to setup

### Create pulumi esc
```bash
➜ esc env init napkin-math/prod
```

### Create pulumi project
```bash
infra/temp git:(main) ✗ 
➜ pulumi new
 Would you like to create a project from a template or using a Pulumi AI prompt? template
Please choose a template (230 total):
 google-native-python               A minimal Google Cloud Python Pulumi program

Project name (temp): napkin-math 

Project description (A minimal Google Cloud Python Pulumi program): Infra for benching common programming operations 

Created project 'napkin-math'

Please enter your desired stack name.
To create a stack in an organization, use the format <org-name>/<stack-name> (e.g. `acmecorp/dev`).
Stack name (dev): libaegis 
Created stack 'libaegis'

The toolchain to use for installing dependencies and running the program uv
The Google Cloud project to deploy into (google-native:project): napkin-math 
```

### Provision an OIDC Provider in Google Cloud for Pulumi Cloud
Follow this [example](https://github.com/pulumi/examples/tree/master/gcp-py-oidc-provider-pulumi-cloud#provisioning-an-oidc-provider-in-google-cloud-for-pulumi-cloud) on how to setup OIDC with GCP and Pulumi.