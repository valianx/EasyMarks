"""Prepare offline; --publish uploads the verified ZIP via the WoW author API."""
import argparse
import hashlib
import json
import os
import re
import sys
from urllib.error import HTTPError, URLError
from urllib.request import HTTPRedirectHandler, Request, build_opener
from uuid import uuid4

from . import package

API = "https://wow.curseforge.com/api"
RETAIL_TYPE_ID = 517


def release_metadata(toc, changelog, tag=""):
    version_match = re.search(r"^## Version: (\d+\.\d+\.\d+(?:-(?:alpha|beta)(?:\.\d+)?)?)$", toc, re.M)
    interface_match = re.search(r"^## Interface: (\d{5,6})$", toc, re.M)
    if not version_match or not interface_match:
        raise ValueError("Release requires a supported version and one Retail Interface value")
    version = version_match.group(1)
    if tag and tag != f"v{version}":
        raise ValueError("Tag must be v followed by the exact TOC version")
    section = re.search(rf"^## {re.escape(version)}\s*\n(.*?)(?=^## |\Z)", changelog, re.M | re.S)
    if not section or not section.group(1).strip():
        raise ValueError("Missing changelog section for this version")
    interface = int(interface_match.group(1))
    game_version = f"{interface // 10000}.{interface // 100 % 100}.{interface % 100}"
    channel = "alpha" if "-alpha" in version else "beta" if "-beta" in version else "release"
    return {
        "displayName": f"Easy Marks {version}",
        "gameVersionNames": [game_version],
        "releaseType": channel,
        "changelog": section.group(1).strip(),
        "changelogType": "markdown",
    }


def retail_version_id(versions, name):
    matches = [item["id"] for item in versions
               if item.get("name") == name and item.get("gameVersionTypeID") == RETAIL_TYPE_ID]
    if len(matches) != 1 or type(matches[0]) is not int or matches[0] <= 0:
        raise ValueError(f"Expected one exact Retail game version: {name}; no fallback is allowed")
    return matches[0]


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        # Never forward the author token to a redirect destination.
        return None


def api_json(path, token, data=None, content_type=None):
    headers = {"X-Api-Token": token, "Accept": "application/json", "User-Agent": "EasyMarks-release"}
    if content_type:
        headers["Content-Type"] = content_type
    request = Request(API + path, data=data, headers=headers)
    try:
        with build_opener(NoRedirect()).open(request, timeout=60) as response:
            return json.load(response)
    except (HTTPError, URLError, TimeoutError, ValueError) as error:
        # One attempt only: the upload API documents no idempotency key.
        status = f"HTTP {error.code}" if isinstance(error, HTTPError) else "connection or response error"
        raise RuntimeError(f"CurseForge {status}. Check the author dashboard before retrying an upload.") from None


def multipart(metadata, filename, content):
    boundary = "EasyMarks" + uuid4().hex
    body = (
        f'--{boundary}\r\nContent-Disposition: form-data; name="metadata"\r\n'
        'Content-Type: application/json\r\n\r\n'
        + json.dumps(metadata, ensure_ascii=False)
        + f'\r\n--{boundary}\r\nContent-Disposition: form-data; name="file"; filename="{filename}"\r\n'
        'Content-Type: application/zip\r\n\r\n'
    ).encode("utf-8") + content + f"\r\n--{boundary}--\r\n".encode()
    return body, f"multipart/form-data; boundary={boundary}"


def upload(metadata, archive, project_id, token):
    if not re.fullmatch(r"[1-9]\d*", project_id) or not token.strip():
        raise ValueError("Set CURSEFORGE_PROJECT_ID and the CF_API_TOKEN secret before publishing")
    package.verify_archive(archive)
    resolved = dict(metadata)
    name = resolved.pop("gameVersionNames")[0]
    versions = api_json("/game/wow/versions", token)
    resolved["gameVersions"] = [retail_version_id(versions, name)]
    content = archive.read_bytes()
    body, content_type = multipart(resolved, archive.name, content)
    result = api_json(f"/projects/{project_id}/upload-file", token, body, content_type)
    if not isinstance(result, dict) or type(result.get("id")) is not int or result["id"] <= 0:
        raise RuntimeError("Upload response has no file ID. Check the author dashboard before retrying.")
    return {"projectId": int(project_id), "fileId": result["id"],
            "filename": archive.name, "sha256": hashlib.sha256(content).hexdigest()}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tag", default="")
    parser.add_argument("--publish", action="store_true", help="Upload a previously prepared ZIP")
    args = parser.parse_args(argv)
    toc = (package.SOURCE / "EasyMarks.toc").read_text(encoding="utf-8")
    changelog = (package.ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    metadata = release_metadata(toc, changelog, args.tag)
    metadata_path = package.ROOT / "dist/curseforge-metadata.json"
    if not args.publish:
        archive = package.main()
        metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"Prepared only: {archive.name}; SHA-256 {hashlib.sha256(archive.read_bytes()).hexdigest()}")
        return
    if not args.tag:
        raise ValueError("Publishing requires an explicit version tag")
    if os.environ.get("GITHUB_RUN_ATTEMPT", "1") != "1":
        raise ValueError("Automatic run retries cannot upload; check CurseForge Files before starting a new run")
    if not metadata_path.is_file() or json.loads(metadata_path.read_text(encoding="utf-8")) != metadata:
        raise ValueError("Prepare the release metadata before uploading")
    archive = package.ROOT / "dist" / f"EasyMarks-{package.read_version()}.zip"
    receipt = upload(metadata, archive, os.environ.get("CURSEFORGE_PROJECT_ID", ""),
                     os.environ.get("CF_API_TOKEN", ""))
    (package.ROOT / "dist/curseforge-receipt.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(f"Uploaded CurseForge file {receipt['fileId']}; approval and visibility are managed by CurseForge.")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, RuntimeError, OSError) as error:
        print(str(error), file=sys.stderr)
        sys.exit(1)
