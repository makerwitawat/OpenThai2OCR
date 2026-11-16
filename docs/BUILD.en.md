# Build & Release — OpenThai2.0 OCR

[ไทย](BUILD.md) | **English**

## Local build (Windows)

```bat
build_exe.bat          :: single file  dist\OpenThai2OCR.exe  (model embedded)
build_exe_onedir.bat   :: folder       dist\OpenThai2OCR\      (faster startup)
```

- **onefile** = easiest to distribute, but extracts to temp on every launch (first page ~2–8 s slower)
- **onedir** = faster startup, but ships the whole folder (`_internal\` + `models\`)

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

3. The `release` workflow builds all three systems and attaches:

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
python -m pytest -q          # 9 API tests
python tools/smoke_test.py   # real OCR smoke test
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
| `build_exe.bat` | Windows onefile build |
| `build_exe_onedir.bat` | Windows onedir build |