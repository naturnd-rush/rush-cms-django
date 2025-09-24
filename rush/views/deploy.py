import hashlib
import hmac
import logging
import subprocess
import sys

import jinja2
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from rush.models import DeployLog, DeployStatus


class DeployRunner:

    NGINX_CONFIG_TEMPLATE_PATH = "nginx.conf.template"

    def __init__(self, needs_auth=True, request=None) -> "DeployRunner":
        self.logger = None
        self.logfile = None
        self.request = request
        self.needs_auth = needs_auth

    def _authenticate(self, request: HttpRequest) -> None:
        """
        Fails if the request signature is invalid.
        """
        if not request:
            raise PermissionDenied
        if signature := request.META.get("HTTP_X_HUB_SIGNATURE_256", None):
            payload = request.body
            sha1_signature = signature.split("=")[-1]
            valid_signature = hmac.new(
                settings.DEPLOY_GITHUB_WEBHOOK_SECRET.encode("utf-8"),
                msg=payload,
                digestmod=hashlib.sha256,
            ).hexdigest()
            if hmac.compare_digest(valid_signature, sha1_signature):
                self.logger.info("Signature valid! Beginning deployment...")
                return
        self.logger.warning(
            "Request for deployment aborted. Invalid signature. %s",
            sha1_signature,
        )
        raise PermissionDenied

    def run(self) -> DeployStatus:
        self.log = DeployLog.objects.create(status=DeployStatus.IN_PROGRESS)
        self.logger: logging.Logger = self.create_logger(self.log)

        try:
            if self.needs_auth:
                self._authenticate(self.request)
            self.execute(f"git -C {self.deploy_dir()} pull origin main")
            self.execute("poetry install")
            self.execute("poetry run python manage.py makemigrations")
            self.execute("poetry run python manage.py migrate")
            self.execute("poetry run python manage.py collectstatic --noinput")
            # self.logger.info("Populating nginx config...")
            # config = self.populate_nginx_config()
            # self.logger.info("Saving nginx config...")
            # with open(settings.DEPLOY_NGINX_CONFIG_PATH, "w") as file:
            #     file.write(config)
            # symlink config to the enabled directory (this enables the site)
            # self.execute(f"ln -sf {settings.DEPLOY_NGINX_CONFIG_PATH} {settings.DEPLOY_NGINX_ENABLED_PATH}")
            self.execute("sudo systemctl restart nginx")
            self.execute("sudo systemctl restart gunicorn")
            self.logger.info("Deployment succeeded.")
            return self.update_status_and_return(DeployStatus.SUCCEEDED)

        except Exception as e:
            self.logger.error(f"Deployment failed!", exc_info=e)
            return self.update_status_and_return(DeployStatus.FAILED)
            # return JsonResponse({"status": DeployStatus.FAILED}, status=500)

    def populate_nginx_config(self) -> str:
        """Render the nginx config using the current ENV vars for deployment."""
        with open(self.NGINX_CONFIG_TEMPLATE_PATH, "r") as file:
            template_content = file.read()
            template = jinja2.Template(template_content)
            return template.render(
                domain=settings.DEPLOY_DOMAIN_NAME,
                gunicorn_sock_path=settings.DEPLOY_GUNICORN_SOCKET_PATH,
                static_root=settings.STATIC_ROOT,
                media_root=settings.MEDIA_ROOT,
            )

    def update_status_and_return(self, status: DeployStatus) -> DeployStatus:
        self.log.status = status
        self.log.full_clean()
        self.log.save()
        return self.log.status

    def deploy_dir(self) -> str:
        """Deploy in a development directory if DEBUG is True. Otherwise, overwrite the current project."""
        dev_dir = f"{settings.BASE_DIR}/.dev-deploy-project-dir"
        return settings.BASE_DIR if not settings.DEBUG else dev_dir

    def execute(self, command: str) -> None:
        """Execute a shell command."""
        self.logger.info(f"Executing: '{command}'...")
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )
        while True:
            line = process.stdout.readline()
            if line == "" and process.poll() is not None:
                # exit condition
                break
            if line and line.strip() != "":
                self.logger.info(line.strip())
        process.wait()

    def create_logger(self, log: DeployLog) -> logging.Logger:
        filepath = log.filepath()
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

        # write logs to the deploy log file
        file_handler = logging.FileHandler(filepath)
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)

        # also write to the console
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)

        # return the logger
        logger = logging.getLogger(__name__)
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        logger.setLevel(logging.INFO)
        return logger


@csrf_exempt
def deploy_webhook_handler(request: HttpRequest) -> JsonResponse:
    """
    Deploy endpoint.
    """
    runner = DeployRunner(needs_auth=True, request=request)
    status = runner.run()
    return JsonResponse({"status": status})
