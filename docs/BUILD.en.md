# Build & Release — OpenThai2.0 OCR

[ไทย](BUILD.md) | **English**

## Local build (Windows)

```bat
build_exe.bat          :: single file  dist\OpenThai2OCR.exe  (model embedded)
build_exe_onedir.bat   :: folder       dist\OpenThai2OCR\      (faster startup)
```

- **onefile** = easiest to distribute, but extracts to temp on every launch (window appears in ~2–3 s)
- **onedir** = faster startup (~1 s), but ships the whole folder (`_internal\` + `models\`)

Both scripts run these steps in order and stop at the first failure:

1. Install dependencies (`requirements.txt` + `-dev` + `-build`)
2. `pytest -q` - skip with `build_exe.bat --skip-tests`
3. PyInstaller (`OpenThai2OCR.spec` / `OpenThai2OCR_onedir.spec`)
4. (onedir) copy `models\` next to the exe
5. **Smoke-test the built exe** - `tools\exe_smoke.py` launches it with `--no-browser --port 5890`,
   waits for `/api/health`, runs one OCR request, then shuts it down (CI runs the same step in `release.yml`)

- Uses `.venv\Scripts\python.exe` when present, otherwise `python` from PATH
- Script messages are English-only (the `.bat` files are pure ASCII) so they never garble on non-Thai Windows
- Both specs drop the same unused files (`_DROP`) and share the WebView2 hidden imports - **change one spec, change the other**
- Run from source: `run_web.bat` (extra arguments are passed to `app.py`)

## Build on Linux / macOS

```bash
python -m pip install -r requirements.txt -r requirements-build.txt
pyinstaller OpenThai2OCR.spec --noconfirm --clean
chmod +x dist/OpenThai2OCR.exe   # on Unix it is a plain binary; rename as you like
```

> PyInstaller does not cross-compile — build on the target OS. The CI workflow
> `.github/workflows/release.yml` does this automatically on every tag.

## Release on all OS (GitHub Actions)

1. Update `CHANGELOG.md` for the version and commit
2. Push a tag

```bash
git tag v1.0.0
git push origin v1.0.0
```

3. On each OS the `release` workflow runs `pytest` -> model check -> build -> **smoke test of the built binary**
   (`tools/exe_smoke.py`) -> (Windows: sign if secrets exist) -> attach to the Release.
   - If any step fails the job stops and `publish` does not run (proven with a throwaway branch containing a failing test)
   - `publish` runs only on a pushed tag (`workflow_dispatch` on a branch lets you test builds without releasing)

   Attached files:

   - `OpenThai2OCR-windows-x64.exe`
   - `OpenThai2OCR-linux-x64`
   - `OpenThai2OCR-macos-<arch>`

Manual release (without waiting for CI):

```bash
gh release create v1.0.0 --notes-file notes.md dist/OpenThai2OCR.exe
python tools/release-notes-patch.py v1.0.0 notes.md --repo <owner>/<repo>
gh release upload v1.0.0 dist/OpenThai2OCR-linux-x64 --clobber
```

> On Windows, `gh --notes-file` reads files as cp874 and garbles Thai. Create the release with
> ASCII notes, then run `tools/release-notes-patch.py` (UTF-8 via GitHub API) and verify the
> `.checked` file with an editor.

## Code signing

A code-signing certificate reduces the "Windows protected your PC" warning.
`tools/sign_exe.ps1` finds `signtool.exe` automatically (PATH or Windows Kits).

```powershell
# 1) .pfx file
$env:SIGN_PFX = "C:\certs\codesign.pfx"; $env:SIGN_PFX_PASSWORD = "secret"
powershell -ExecutionPolicy Bypass -File tools\sign_exe.ps1 -Path dist\OpenThai2OCR.exe

# 2) certificate installed in the Windows store (thumbprint)
$env:SIGN_THUMBPRINT = "A1B2C3..."
powershell -ExecutionPolicy Bypass -File tools\sign_exe.ps1
```

- Sign **before** renaming/uploading (CI signs before the Rename step)
- Optional `-TimestampUrl` (default `http://timestamp.digicert.com`)
- The script runs `signtool verify /pa` and stops if verification fails

For CI set the secrets `WINDOWS_PFX_BASE64` (base64 of the .pfx) and
`WINDOWS_PFX_PASSWORD`; the `release` workflow then signs the Windows exe
automatically (the step is skipped when the secret is absent).

## Test before building

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q          # API / export / etc. (39 tests)
python tools/smoke_test.py   # real OCR smoke test from source
python tools/exe_smoke.py dist/OpenThai2OCR.exe   # smoke-test a built exe/binary (--port, --timeout)
```

## Models and assets

`models/` holds `det.onnx`, `rec.onnx`, `rec_dict.txt`, `config.json`. The onefile spec embeds them.

`assets/` holds `NotoSansThai-Regular.ttf` (OFL) used for the searchable PDF export — also embedded.

Download/refresh from Hugging Face:

```bash
python tools/download_models.py
```

## Build files

| File | Purpose |
|---|---|
| `OpenThai2OCR.spec` | onefile (model embedded) — used by CI |
| `OpenThai2OCR_onedir.spec` | onedir |
| `app.ico` | exe icon |
| `build_exe.bat` | Windows onefile build (tests -> build -> smoke-test the exe) |
| `build_exe_onedir.bat` | Windows onedir build (tests -> build -> copy models -> smoke-test the exe) |
| `run_web.bat` | Run from source on Windows (checks Python/dependencies) |
| `tools/exe_smoke.py` | Smoke test for a built binary (used by the `.bat` files and CI) |