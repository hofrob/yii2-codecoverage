#!/usr/bin/env python3
import argparse
import subprocess
import sys
import os

class DockerManager():
    WORKING_DIRECTORY = "/code"
    PHP_FPM_DIRECTORY = "/usr/local/etc/php-fpm.d"
    DOCKER_DIRECTORY = "/docker"
    APPLICATION_USER = "application"

    def __init__(self):
        parser = argparse.ArgumentParser(
            description="Docker Manage Script",
            usage="""
Possible Commands
   bash - drop to bash (passes arguments)
   clean - deletes the vendor folder
   composer - run composer command (passes arguments)
   fix_permissions - change all permissions in the root folder to the current user
   fixtures - shortcut for handling fixtures (create / load)
   lint - checks the code with phpcs
   migrate - shortcut for migrations (passes arguments)
   nodejs - calls nodejs (passes arguments)
   npm - calls npm (passes arguments)
   php - runs php commands (passes arguments)
   serve - starts the webserver
   test - run tests with arguments (passes arguments)
   yii - run a yii command (passes arguments)
"""
        )

        commands = [f for f in dir(self) if callable(getattr(self, f)) and not f.startswith("_")]
        parser.add_argument("command", help="Subcommand to run", choices=commands)

        params = parser.parse_args(sys.argv[1:2])

        if params.command.startswith("_") or not hasattr(self, params.command):
            print("Unrecognized Command!")
            parser.print_help()
            exit(1)

        getattr(self, params.command)(*sys.argv[2:])

        if params.command != "fix_permissions":
            self.fix_permissions()

    def _run_command(self, *args, **kwargs):
        options = {
            "cwd" : self.WORKING_DIRECTORY,
            "universal_newlines" : True,
        }

        options.update(kwargs)

        process = subprocess.Popen(args, **options)
        process.communicate()

        return process.returncode

    def _get_uid_gid(self):
        uid = os.environ.get("HTTP_USER")
        gid = os.environ.get("HTTP_GROUP")

        if not uid or not gid:
            print("HTTP_USER and / or HTTP_GROUP are not set!")
            exit(1)

        return uid, gid

    """
        SUBCOMMANDS
    """
    def yii(self, *args):
        self._run_command("./yii", *args)

    def init(self, *args):
        self._run_command("./init", *args)

    def composer(self, *args):
        self._run_command("chown", "-R", self.APPLICATION_USER + ":", "/code")
        self._run_command("gosu", self.APPLICATION_USER, "composer", *args)

    def test(self, *args):
        database_host = os.environ.get("POSTGRES_HOST")
        database_port = os.environ.get("POSTGRES_PORT")

        self.wait(database_host + ":" + database_port)
        self.migrate("--interactive=0")

        return_code = self._run_command("codecept", "run", *args)

        self.fix_permissions()

        exit(return_code)

    def bash(self, *args):
        self._run_command("gosu", self.APPLICATION_USER, "bash", *args)

    def migrate(self, *args):
        self.yii("migrate", *args)

    def php(self, *args):
        self._run_command("php", *args)

    def serve(self, *args):
        self._run_command("envsubst '\$HTTP_USER,\$HTTP_GROUP' < usergroup.conf.default > www.conf ", shell=True, cwd=self.PHP_FPM_DIRECTORY)
        self._run_command("php-fpm")

    def wait(self, *args):
        self._run_command("./wait-for-it.sh", *args, cwd=self.DOCKER_DIRECTORY)

    def fix_permissions(self, *args):
        dont_fix_permissions = os.path.isfile("/code/.dont_fix_permissions")

        if dont_fix_permissions:
            return

        uid, gid = self._get_uid_gid()
        user_group = "{user}:{group}".format(user=uid, group=gid)

        print("Fixing Permissions")
        self._run_command("chown", "-R", user_group, self.WORKING_DIRECTORY)

    def clean(self, *args):
        self._run_command("rm", "-rf", "vendor/")

if __name__ == "__main__":
    DockerManager()

