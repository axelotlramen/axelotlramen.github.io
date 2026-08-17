import nox

nox.options.default_venv_backend = "uv"


def _uv_sync(session, *groups):
    args = ["uv", "sync", "--locked"]
    for group in groups:
        args += ["--group", group]
    session.run_install(*args, env={"UV_PROJECT_ENVIRONMENT": session.virtualenv.location})


@nox.session
def lint(session):
    _uv_sync(session, "lint")
    session.run("ruff", "check", ".")


@nox.session
def typecheck(session):
    _uv_sync(session, "typecheck")
    session.run("pyright")


@nox.session
def run(session):
    _uv_sync(session)
    session.run("python", "-m", "scripts.update_stats")


@nox.session
def test(session):
    _uv_sync(session, "test")
    session.run("pytest")
