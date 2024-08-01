import argparse
import http
import json
import sys
from enum import Enum
from typing import Any, Optional

import requests


class UpdateStatus(Enum):
    SUCCESS = 0
    FAILURE = 1


def get_robot_id(args: Any) -> Optional[int]:
    header = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Api-Key": args.key,
    }
    url = f"{args.url}/v1/robots"
    get_response = requests.get(url, headers=header)
    if not http.HTTPStatus(get_response.status_code).is_success:
        sys.exit(f"Request failed with status code {get_response.status_code}.")

    for robot in get_response.json():
        if robot["serialNumber"] == int(args.robotnumber):
            return robot["id"]


def update_robot(args: Any) -> UpdateStatus:
    header = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Api-Key": args.key,
    }
    robot_id = get_robot_id(args)
    if not robot_id:
        print(f"Could not find robot '{args.robotnumber}' on the backend.")
        return UpdateStatus.FAILURE

    print(f"Updating the password of robot '{args.robotnumber}' on the backend.")
    user_data = {
        "password": args.password,
    }
    patch_response = requests.patch(
        f"{args.url}/v1/users/{robot_id}",
        headers=header,
        data=json.dumps(user_data),
    )
    if not http.HTTPStatus(patch_response.status_code).is_success:
        return UpdateStatus.FAILURE

    return UpdateStatus.SUCCESS


def register_robot(args: Any) -> None:
    header = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Api-Key": args.key,
    }
    access_groups = ["cartken-robots", "magna"]
    data = {
        "password": args.password,
        "serialNumber": int(args.robotnumber),
        "shortName": str(args.robotnumber),
    }
    if args.operation is not None:
        data["assignedOperationId"] = args.operation
        access_groups.append(args.operation)

    data["accessGroups"] = access_groups
    url = f"{args.url}/v1/robots"
    print(f"Creating new robot '{args.robotnumber}' on the backend.")
    post_response = requests.post(url, headers=header, data=json.dumps(data))
    if not http.HTTPStatus(post_response.status_code).is_success:
        sys.exit(f"Failed to create a new robot '{args.robotnumber}' on the backend.")


def main():
    parser = argparse.ArgumentParser(prog="backend-interface")
    parser.add_argument("--key", required=True, help="Key to the backend")
    parser.add_argument("--url", required=True, help="Which url to use (staging or prod)")
    parser.add_argument("--password", required=True, help="(New) password")
    parser.add_argument(
        "--robotnumber",
        required=True,
        help="Number of the (new) cart",
    )
    parser.add_argument(
        "--operation",
        required=False,
        help="Operation the robot should be assigned to (optional)",
    )
    args = parser.parse_args()

    if update_robot(args) == UpdateStatus.FAILURE:
        register_robot(args)


if __name__ == "__main__":
    main()
