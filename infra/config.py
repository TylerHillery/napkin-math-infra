import pulumi


class Settings:
    STACK_NAME: str = pulumi.get_stack()
    PROJECT_NAME: str = pulumi.get_project()
    ORG_NAME: str = pulumi.get_organization()

    github_config: pulumi.Config = pulumi.Config("github")
    GITHUB_USERNAME: str = github_config.get("username") or "TylerHillery"
    GITHUB_OIDC_ISSUER: str = (
        github_config.get("oidc-issuer")
        or "https://token.actions.githubusercontent.com"
    )

    project_config: pulumi.Config = pulumi.Config()

    pulumi_config: pulumi.Config = pulumi.Config("pulumi")
    PULUMI_ACCESS_TOKEN: pulumi.Output | None = pulumi_config.get_secret("token")
    PULUMI_OIDC_ISSUER: str = (
        pulumi_config.get("oidc-issuer") or "https://api.pulumi.com/oidc"
    )

settings = Settings()
