#!/usr/bin/env python3

import argparse
import logging
import os
import re
import sys

from playstore.playstore import Playstore

# Logging configuration.
logger = logging.getLogger(__name__)
logging.basicConfig(
    format="%(asctime)s> [%(levelname)s][%(name)s][%(funcName)s()] %(message)s",
    datefmt="%d/%m/%Y %H:%M:%S",
    level=logging.INFO,
)

downloaded_apk_default_location = "/tmp"


def get_cmd_args(args: list = None):
    """
    Parse and return the command line parameters needed for the script execution.

    :param args: Optional list of arguments to be parsed (by default sys.argv is used).
    :return: The command line needed parameters.
    """
    parser = argparse.ArgumentParser(
        description="Download an application (.apk) from the Google Play Store."
    )
    parser.add_argument(
        "-b",
        "--blobs",
        action="store_true",
        help="Download the additional .obb files along with the application (if any)",
    )
    parser.add_argument(
        "-s",
        "--split-apks",
        action="store_true",
        help="Download the additional split apks along with the application (if any)",
    )
    parser.add_argument(
        "-o",
        "--out",
        type=str,
        metavar="FILE",
        default=downloaded_apk_default_location + "/" + os.environ["APP_PACKAGE"] + ".apk",
        help="The path where to save the downloaded .apk file. By default the file "
        'will be saved in a "Downloads/" directory created where this script '
        "is run",
    )
    parser.add_argument(
        "-t",
        "--tag",
        type=str,
        metavar="TAG",
        help='An optional tag prepended to the file name, e.g., "[TAG] filename.apk"',
    )
    return parser.parse_args(args)



def main():
    args = get_cmd_args()
    credential =   {
        "USERNAME": os.environ["APP_USERNAME"],
        "PASSWORD": os.environ["APP_PASSWORD"],
        "ANDROID_ID": os.environ["APP_ANDROID_ID"],
        "LANG_CODE": os.environ["APP_LANG_CODE"],
        "LANG": os.environ["APP_LANG_CODE"]
    }
    try:
        api = Playstore(credential)
        stripped_package_name = os.environ["APP_PACKAGE"]
        try:
            app = api.app_details(stripped_package_name).docV2
        except AttributeError:
            logger.critical(
                f"Error when downloading '{stripped_package_name}': unable to "
                f"get app's details"
            )
            sys.exit(1)

        details = {
            "package_name": app.docid,
            "title": app.title,
            "creator": app.creator,
        }

        if args.out.strip(" '\"") == downloaded_apk_default_location:
            downloaded_apk_file_path = os.path.join(
                downloaded_apk_default_location,
                re.sub(
                    r"[^\w\-_.\s]",
                    "_",
                    f"{details['title']} by {details['creator']} - "
                    f"{details['package_name']}.apk",
                ),
            )
        else:
            downloaded_apk_file_path = os.path.abspath(args.out.strip(" '\""))
        if not os.path.isdir(os.path.dirname(downloaded_apk_file_path)):
            os.makedirs(os.path.dirname(downloaded_apk_file_path), exist_ok=True)

        if args.tag and args.tag.strip(" '\""):
            stripped_tag = args.tag.strip(" '\"")
            downloaded_apk_file_path = os.path.join(
                os.path.dirname(downloaded_apk_file_path),
                f"[{stripped_tag}] {os.path.basename(downloaded_apk_file_path)}",
            )
        success = api.download(
            details["package_name"],
            downloaded_apk_file_path,
            download_obb=True if args.blobs else False,
            download_split_apks=True if args.split_apks else False,
        )

        if not success:
            logger.critical(f"Error when downloading '{details['package_name']}'")
            sys.exit(1)

    except Exception as ex:
        logger.critical(f"Error during the download: {ex}")
        sys.exit(1)
if __name__ == "__main__":
    main()