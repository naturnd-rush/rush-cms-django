import hashlib
import hmac
import logging
import os
import subprocess
import sys
from datetime import datetime

from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from jinja2 import Template

from rush.models import DeployLog


def _get_deploy_file_logger(directory: str, file_prefix: str) -> logging.Logger:
    """
    Get logger that writes to a timestamped file in the given directory.
    """
    os.makedirs(directory, exist_ok=True)
    log_filename = f'{file_prefix}{datetime.now().strftime("%Y-%m-%d_%H:%M:%S")}.log'
    DeployLog.objects.create(filename=log_filename)
    log_filepath = os.path.join(directory, log_filename)
    latest_log_filepath = os.path.join(directory, "latest.log")

    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    file_handler = logging.FileHandler(log_filepath)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)

    # also write to latest.log for easy access
    latest_log_file_handler = logging.FileHandler(latest_log_filepath)
    latest_log_file_handler.setLevel(logging.INFO)
    latest_log_file_handler.setFormatter(formatter)

    # also write to console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    logger = logging.getLogger(__name__)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    logger.setLevel(logging.INFO)
    return logger


def run_command(command, logger, capture_output=False):
    """
    Run a shell command and capture the output or raise error on failure.
    """
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            text=True,
            capture_output=capture_output,
        )
        if result.stdout:
            logger.info(f"STDOUT: {result.stdout}")
        if capture_output:
            return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        if result.stderr:
            logger.error(f"STDERR: {result.stderr}")
        logger.error(f"Error running command: {e.args}")
        sys.exit(1)


def _auth_deploy_request(request: HttpRequest, logger) -> None:
    """
    Authenticate the deploy request by returning 403 (Permission Denied)
    if the hashed payload (request body) doesn't match the request signature.
    """
    logger.info("request meta: %s", request.META)
    if signature := request.META.get("HTTP_X_HUB_SIGNATURE_256", None):
        sha1_signature = signature.split("=")[-1]
        valid_signature = hmac.new(
            bytes(settings.GITHUB_WEBHOOK_SECRET, "utf-8"),
            msg=request.body,
            digestmod=hashlib.sha1,
        ).hexdigest()
        logger.info(
            "incoming sig %s, valid sig %s, and payload %s",
            sha1_signature,
            valid_signature,
            request.body,
        )
        if hmac.compare_digest(valid_signature, sha1_signature):
            return
    logger.warning("Request for deployment aborted. Invalid signature. %s", request)
    raise PermissionDenied


def _deploy(logger: logging.Logger) -> JsonResponse:
    """
    Deploy the admin site.
    """
    try:
        logger.info("Deploying...")
        project_dir = settings.BASE_DIR
        if settings.DEBUG == True:
            # for local testing
            project_dir = f"{project_dir}/.dev-deploy-project-dir"

        logger.info("Pulling repo...")
        os.makedirs(project_dir, exist_ok=True)
        run_command(f"git -C {project_dir} pull origin main", logger)

        logger.info("Installing dependencies...")
        run_command(f"poetry install", logger, capture_output=False)

        logger.info("Making migrations...")
        run_command(
            f"poetry run python manage.py makemigrations",
            logger,
            capture_output=False,
        )

        logger.info("Migrating...")
        run_command(
            f"poetry run python manage.py migrate",
            logger,
            capture_output=False,
        )

        logger.info("Collecting staticfiles...")
        run_command(
            f"poetry run python manage.py collectstatic --noinput",
            logger,
            capture_output=False,
        )

        logger.info("Building nginx config...")
        with open("nginx.conf", "r") as template_file:
            template_content = template_file.read()
        template = Template(template_content)
        nginx_config = template.render(
            # allowed_hosts=" ".join(settings.ALLOWED_HOSTS),
            domain=settings.DEPLOY_DOMAIN_NAME,
            # project_dir=project_dir,
            gunicorn_sock_path=settings.DEPLOY_GUNICORN_SOCKET_PATH,
            static_root=settings.STATIC_ROOT,
            media_root=settings.MEDIA_ROOT,
        )
        with open(settings.DEPLOY_NGINX_CONFIG_PATH, "w") as f:
            f.write(nginx_config)
        run_command(
            f"ln -sf {settings.DEPLOY_NGINX_CONFIG_PATH} {settings.DEPLOY_NGINX_ENABLED_PATH}",
            logger,
        )

        logger.info("Restarting services...")
        run_command("sudo systemctl restart nginx", logger, capture_output=False)
        run_command("sudo systemctl restart gunicorn", logger, capture_output=False)

        logger.info("Deployment completed successfully!")
        return JsonResponse({"status": "success"})

    except Exception as e:
        logger.error(f"Deployment failed: {e}")
        return JsonResponse({"status": "failed"}, status=500)


@csrf_exempt
def deploy_webhook_handler(request: HttpRequest) -> JsonResponse:
    """
    Deploy view with request authentication.
    """

    logger = _get_deploy_file_logger(settings.DEPLOY_LOGS_DIR, "deploy_")
    _auth_deploy_request(request, logger)
    _deploy(logger)
