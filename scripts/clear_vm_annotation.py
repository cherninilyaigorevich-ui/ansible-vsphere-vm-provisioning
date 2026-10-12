#!/usr/bin/env python3

import argparse
import os
import ssl
import sys
import time

from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim


def wait_for_task(task):
    while task.info.state in (
        vim.TaskInfo.State.queued,
        vim.TaskInfo.State.running,
    ):
        time.sleep(1)

    if task.info.state == vim.TaskInfo.State.error:
        raise RuntimeError(str(task.info.error))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--vm-name", required=True)
    args = parser.parse_args()

    hostname = os.environ.get("VMWARE_HOST")
    username = os.environ.get("VMWARE_USER")
    password = os.environ.get("VMWARE_PASSWORD")

    if not all((hostname, username, password)):
        print(
            "ERROR: VMWARE_HOST, VMWARE_USER and VMWARE_PASSWORD "
            "must be defined",
            file=sys.stderr,
        )
        return 2

    context = ssl._create_unverified_context()

    si = SmartConnect(
        host=hostname,
        user=username,
        pwd=password,
        sslContext=context,
    )

    try:
        content = si.RetrieveContent()

        view = content.viewManager.CreateContainerView(
            content.rootFolder,
            [vim.VirtualMachine],
            True,
        )

        try:
            matches = [
                vm for vm in view.view
                if vm.name == args.vm_name
            ]
        finally:
            view.Destroy()

        if len(matches) != 1:
            print(
                f"ERROR: expected exactly one VM named "
                f"'{args.vm_name}', found {len(matches)}",
                file=sys.stderr,
            )
            return 3

        vm = matches[0]
        current_annotation = vm.config.annotation

        if current_annotation in (None, ""):
            print(
                f"UNCHANGED: annotation already empty "
                f"for '{args.vm_name}'"
            )
            return 0

        spec = vim.vm.ConfigSpec()
        spec.annotation = ""

        task = vm.ReconfigVM_Task(spec=spec)
        wait_for_task(task)

        print(
            f"CHANGED: annotation cleared for '{args.vm_name}'"
        )
        return 0

    finally:
        Disconnect(si)


if __name__ == "__main__":
    sys.exit(main())
