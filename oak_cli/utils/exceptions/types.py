from oak_cli.utils.types import CustomEnum


class OakCLIExceptionTypes(CustomEnum):
    LOGIN = "Login"
    APP_CREATE = "Application Creation"
    APP_DELETE = "Application Deletion"
    APP_GET = "GET Application"
    SERVICE_GET = "GET Service"
    SERVICE_DEPLOYMENT = "Deploying Service"
    SERVICE_UNDEPLOYMENT = "Undeploying Service"
    FLOPS_PLUGIN = "FLOps Plugin"
