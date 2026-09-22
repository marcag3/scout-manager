#!/usr/bin/env python3
import argparse
import os
import subprocess


def cprint(*args, level: int = 1):
	COLOR = {1: "\033[31m", 2: "\33[92m", 3: "\33[93m"}[level]
	reset = "\033[0m"
	print(COLOR, " ".join(map(str, args)), reset)


def main():
	parser = get_args_parser()
	args = parser.parse_args()
	init_bench_if_not_exist(args)
	create_site_in_bench(args)


def get_args_parser():
	parser = argparse.ArgumentParser()
	parser.add_argument(
		"-j",
		"--apps-json",
		action="store",
		type=str,
		help="Path to apps.json, default: apps-example.json",
		default="apps-example.json",
	)
	parser.add_argument(
		"-b",
		"--bench-name",
		action="store",
		type=str,
		help="Bench directory name, default: frappe-bench",
		default="frappe-bench",
	)
	parser.add_argument(
		"-s",
		"--site-name",
		action="store",
		type=str,
		help="Site name, should end with .localhost, default: development.localhost",
		default="development.localhost",
	)
	parser.add_argument(
		"-r",
		"--frappe-repo",
		action="store",
		type=str,
		help="frappe repo to use, default: https://github.com/frappe/frappe",
		default="https://github.com/frappe/frappe",
	)
	parser.add_argument(
		"-t",
		"--frappe-branch",
		action="store",
		type=str,
		help="frappe repo to use, default: version-16",
		default="version-16",
	)
	parser.add_argument(
		"-p",
		"--py-version",
		action="store",
		type=str,
		help="python version, default: Not Set",
		default=None,
	)
	parser.add_argument(
		"-n",
		"--node-version",
		action="store",
		type=str,
		help="node version, default: Not Set",
		default=None,
	)
	parser.add_argument(
		"-v",
		"--verbose",
		action="store_true",
		help="verbose output",
	)
	parser.add_argument(
		"-a",
		"--admin-password",
		action="store",
		type=str,
		help="admin password for site, default: admin",
		default="admin",
	)
	parser.add_argument(
		"-d",
		"--db-type",
		action="store",
		type=str,
		help="Database type to use (e.g., mariadb or postgres)",
		default="mariadb",
	)
	return parser


def init_bench_if_not_exist(args):
	if os.path.exists(args.bench_name):
		cprint("Bench already exists. Only site will be created", level=3)
		return

	try:
		env = os.environ.copy()
		if args.py_version:
			env["PYENV_VERSION"] = args.py_version

		init_command = ""
		if args.node_version:
			init_command = f"nvm use {args.node_version};"
		if args.py_version:
			init_command += f"PYENV_VERSION={args.py_version} "
		init_command += "bench init "
		init_command += "--skip-redis-config-generation "
		init_command += "--verbose " if args.verbose else " "
		init_command += f"--frappe-path={args.frappe_repo} "
		init_command += f"--frappe-branch={args.frappe_branch} "
		init_command += f"--apps_path={args.apps_json} "
		init_command += args.bench_name

		subprocess.check_call(
			["/bin/bash", "-i", "-c", init_command],
			env=env,
			cwd=os.getcwd(),
		)

		bench_path = os.path.join(os.getcwd(), args.bench_name)
		cprint("Configuring Bench ...", level=2)
		subprocess.check_call(
			["bench", "set-config", "-g", "db_host", "mariadb"],
			cwd=bench_path,
		)
		subprocess.check_call(
			["bench", "set-config", "-g", "redis_cache", "redis://redis-cache:6379"],
			cwd=bench_path,
		)
		subprocess.check_call(
			["bench", "set-config", "-g", "redis_queue", "redis://redis-queue:6379"],
			cwd=bench_path,
		)
		subprocess.check_call(
			["bench", "set-config", "-g", "redis_socketio", "redis://redis-queue:6379"],
			cwd=bench_path,
		)
		subprocess.check_call(
			["bench", "set-config", "-gp", "developer_mode", "1"],
			cwd=bench_path,
		)
	except subprocess.CalledProcessError as e:
		cprint(e, level=1)
		raise


def create_site_in_bench(args):
	bench_path = os.path.join(os.getcwd(), args.bench_name)
	site_path = os.path.join(bench_path, "sites", args.site_name)

	if os.path.exists(site_path):
		cprint(f"Site {args.site_name} already exists", level=3)
		return

	subprocess.check_call(
		["bench", "set-config", "-g", "db_host", "mariadb"],
		cwd=bench_path,
	)

	new_site_cmd = [
		"bench",
		"new-site",
		"--db-root-username=root",
		"--db-host=mariadb",
		"--db-type=mariadb",
		"--mariadb-user-host-login-scope=%",
		"--db-root-password=123",
		f"--admin-password={args.admin_password}",
	]

	apps = os.listdir(os.path.join(bench_path, "apps"))
	apps.remove("frappe")
	for app in apps:
		new_site_cmd.append(f"--install-app={app}")

	new_site_cmd.append(args.site_name)
	cprint(f"Creating site {args.site_name} ...", level=2)
	subprocess.check_call(new_site_cmd, cwd=bench_path)


if __name__ == "__main__":
	main()
