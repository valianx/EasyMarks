"""Release contract tests; no real token, network, repository or upload."""
from contextlib import redirect_stdout
from email import policy
from email.parser import BytesParser
import io
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch
from urllib.error import HTTPError
from zipfile import ZipFile

from tools import package, release


class ReleaseTests(unittest.TestCase):
    def metadata(self, version="0.1.10-alpha", tag=""):
        return release.release_metadata(
            f"## Version: {version}\n## Interface: 120100\n",
            f"# Changes\n\n## {version}\n\n- Nueva versión.\n\n## 0.1.9-alpha\n- Old.\n", tag)

    def archive(self, directory):
        path = Path(directory) / f"EasyMarks-{package.read_version()}.zip"
        with ZipFile(path, "w") as archive:
            for name in package.FILES:
                archive.writestr(f"EasyMarks/{name}", (package.SOURCE / name).read_bytes())
        return path

    def test_release_type_version_and_changelog_are_consistent(self):
        for version, channel in (("1.2.3-alpha", "alpha"), ("1.2.3-beta.2", "beta"), ("1.2.3", "release")):
            with self.subTest(version=version):
                data = self.metadata(version, f"v{version}")
                self.assertEqual(data["releaseType"], channel)
                self.assertEqual(data["gameVersionNames"], ["12.1.0"])
                self.assertEqual(data["changelog"], "- Nueva versión.")

    def test_invalid_tag_version_interface_or_missing_changelog_is_rejected(self):
        for tag in ("v0.1.9-alpha", "0.1.10-alpha", "main", "v1.0.0\nunsafe"):
            with self.subTest(tag=tag), self.assertRaises(ValueError):
                self.metadata(tag=tag)
        for toc, changelog in (("## Version: unknown\n## Interface: 120100\n", ""),
                               ("## Version: 1.0.0\n## Interface: 120100,110000\n", "## 1.0.0\nchange"),
                               ("## Version: 1.0.0\n## Interface: 120100\n", "## 0.9.0\nold")):
            with self.subTest(toc=toc), self.assertRaises(ValueError):
                release.release_metadata(toc, changelog)

    def test_game_version_requires_exact_retail_match_without_fallback(self):
        versions = [{"id": 10, "name": "12.1.0", "gameVersionTypeID": 517},
                    {"id": 11, "name": "12.1.0", "gameVersionTypeID": 67408},
                    {"id": 12, "name": "12.0.0", "gameVersionTypeID": 517}]
        self.assertEqual(release.retail_version_id(versions, "12.1.0"), 10)
        for candidates in ([], versions[1:], versions + [versions[0]]):
            with self.subTest(candidates=candidates), self.assertRaises(ValueError):
                release.retail_version_id(candidates, "12.1.0")

    def test_prepare_builds_runtime_only_without_network_or_credentials(self):
        with TemporaryDirectory() as directory, patch.object(release, "api_json") as api:
            root = Path(directory)
            (root / "CHANGELOG.md").write_bytes((package.ROOT / "CHANGELOG.md").read_bytes())
            with patch.object(package, "ROOT", root), redirect_stdout(io.StringIO()):
                release.main([])
                archive = root / "dist" / f"EasyMarks-{package.read_version()}.zip"
                package.verify_archive(archive)
                expected = release.release_metadata(
                    (package.SOURCE / "EasyMarks.toc").read_text(encoding="utf-8"),
                    (root / "CHANGELOG.md").read_text(encoding="utf-8"))
                self.assertEqual(json.loads((root / "dist/curseforge-metadata.json").read_text(encoding="utf-8")), expected)
            api.assert_not_called()

    def test_upload_sends_the_verified_zip_with_resolved_id_and_keeps_a_receipt(self):
        with TemporaryDirectory() as directory:
            archive = self.archive(directory)
            responses = [[{"id": 456, "name": "12.1.0", "gameVersionTypeID": 517}], {"id": 789}]
            with patch.object(release, "api_json", side_effect=responses) as api:
                receipt = release.upload(self.metadata(), archive, "123", "test-token")
            self.assertEqual(api.call_count, 2)
            self.assertEqual(api.call_args_list[0].args[:2], ("/game/wow/versions", "test-token"))
            path, token, body, content_type = api.call_args_list[1].args
            self.assertEqual(path, "/projects/123/upload-file")
            message = BytesParser(policy=policy.default).parsebytes(
                f"MIME-Version: 1.0\r\nContent-Type: {content_type}\r\n\r\n".encode() + body)
            metadata_part, file_part = list(message.iter_parts())
            data = json.loads(metadata_part.get_payload(decode=True))
            self.assertEqual(data["gameVersions"], [456])
            self.assertNotIn("gameVersionNames", data)
            self.assertEqual(file_part.get_payload(decode=True), archive.read_bytes())
            self.assertNotIn(token.encode(), body)
            self.assertEqual((receipt["fileId"], receipt["projectId"]), (789, 123))
            self.assertEqual(len(receipt["sha256"]), 64)

    def test_wrong_package_or_missing_credentials_never_reaches_api(self):
        with TemporaryDirectory() as directory, patch.object(release, "api_json") as api:
            archive = self.archive(directory)
            for project, token in (("", "token"), ("123/unsafe", "token"), ("123", "")):
                with self.subTest(project=project, token=token), self.assertRaises(ValueError):
                    release.upload(self.metadata(), archive, project, token)
            with ZipFile(archive, "a") as changed:
                changed.writestr("private.txt", "must not upload")
            with self.assertRaises(ValueError):
                release.upload(self.metadata(), archive, "123", "test-token")
            api.assert_not_called()

    def test_changed_runtime_bytes_are_rejected(self):
        with TemporaryDirectory() as directory:
            archive = Path(directory) / "modified.zip"
            with ZipFile(archive, "w") as changed:
                for name in package.FILES:
                    content = (package.SOURCE / name).read_bytes()
                    changed.writestr(f"EasyMarks/{name}", content + b"changed" if name == "Core.lua" else content)
            with self.assertRaises(ValueError):
                package.verify_archive(archive)

    def test_upload_errors_are_not_retried_and_do_not_echo_response_secrets(self):
        error = HTTPError("https://wow.curseforge.com/api/test", 500, "test-token", {}, io.BytesIO(b"test-token"))
        with patch.object(release, "build_opener") as opener:
            opener.return_value.open.side_effect = error
            with self.assertRaises(RuntimeError) as caught:
                release.api_json("/test", "test-token", b"payload")
            self.assertNotIn("test-token", str(caught.exception))
            opener.return_value.open.assert_called_once()
        self.assertIsNone(release.NoRedirect().redirect_request(None, None, 302, "", {}, "https://example.com"))

    def test_publish_requires_a_tag_and_refuses_run_retries(self):
        with patch.object(release, "upload") as upload:
            with self.assertRaisesRegex(ValueError, "explicit version tag"):
                release.main(["--publish"])
            with patch.dict(release.os.environ, {"GITHUB_RUN_ATTEMPT": "2"}):
                with self.assertRaisesRegex(ValueError, "retries cannot upload"):
                    release.main(["--publish", "--tag", f"v{package.read_version()}"])
            upload.assert_not_called()
