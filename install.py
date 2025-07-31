import os
import shutil
import stat
import sys


def install_cli_tool(
    script_path="wireguard_cli.py", target_name="wg-cli"
):
    if not os.path.isfile(script_path):
        print(f"File not found: {script_path}")
        sys.exit(1)

    st = os.stat(script_path)
    os.chmod(script_path, st.st_mode | stat.S_IEXEC)
    print(f"Made {script_path} executable")

    system_target = f"/usr/local/bin/{target_name}"

    try:
        shutil.copy(script_path, system_target)
        os.chmod(system_target, os.stat(system_target).st_mode | stat.S_IEXEC)
        print(f"Installed CLI system-wide: {system_target}")
        print(f"Now you can run: {target_name} disconnect")
        return
    except PermissionError:
        print("Permission denied for system-wide installation.")
        print("Installing to user directory instead...")

    user_bin = os.path.expanduser("~/.local/bin")

    os.makedirs(user_bin, exist_ok=True)

    user_target = os.path.join(user_bin, target_name)

    try:
        shutil.copy(script_path, user_target)
        os.chmod(user_target, os.stat(user_target).st_mode | stat.S_IEXEC)
        print(f"Installed CLI to user directory: {user_target}")

        path_dirs = os.environ.get("PATH", "").split(":")
        if user_bin not in path_dirs:
            print(f"{user_bin} is not in your PATH.")
            print("Add this line to your ~/.bashrc or ~/.zshrc:")
            print(f'export PATH="$PATH:{user_bin}"')
            print("Then run: source ~/.bashrc (or restart your terminal)")

        print(f"👉 Now you can run: {target_name} disconnect")

    except Exception as e:
        print(f"Failed to install: {e}")
        sys.exit(1)


if __name__ == "__main__":
    install_cli_tool()
