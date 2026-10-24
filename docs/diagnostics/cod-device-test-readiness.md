# iPhone test readiness — GamingLaptop, 2026-10-24

Read-only inspection of authorized device `303b4e30-70cb-4314-9c91-2da20202fdea` (GamingLaptop). No repository/Actions changes, app launches, installations, tunnels, security changes, or pairing-secret reads were performed.

**No recognized connected iPhone USB test interface was detected.** `Get-PnpDevice -PresentOnly` returned no matching iPhone, Apple Mobile, or Apple USB device. An independent CIM check of present PnP devices by Apple manufacturer/name also returned no matches. This establishes no currently recognized interface; physical cable connection and the phone's trust/unlock state were not tested.

| Component | Observed state |
| --- | --- |
| Apple Mobile Device Service | Running, Automatic |
| iTunes | 12.13.11.1, `C:\Program Files\iTunes\` |
| Apple Mobile Device Support | 20.0.0.35, `C:\Program Files\Common Files\Apple\Mobile Device Support\` |
| PlumeImpactor | 2.7.0, `C:\Program Files\PlumeImpactor\plumeimpactor.exe` |
| Apple Devices Store app | No matching installed AppX package found |
| AltServer / Sideloadly | No matching uninstall metadata, PATH command, or checked standard installation directory found |
| `idevice_id`, `ideviceinstaller`, `ideviceinfo`, `iproxy`, `pymobiledevice3` | Not on PATH; no matching helper executable found in checked Apple/Plume installation trees (depth 2) |
| Python `pymobiledevice3`, `tidevice`, `pyiosdevice`, `libimobiledevice` distributions | Not installed in the default Python 3.13 environment |

Installed software was inspected only through package/registry metadata and executable filenames/version metadata. No pairing records, certificates, Apple IDs, signing credentials, or secret files were inspected. Their presence, validity, and readiness remain unverified.

The new IPA was still building during this inspection and no artifact was installed. Device-level launch/game testing cannot presently proceed through an observed USB interface. A later connected-device check would be needed once an iPhone is recognized and the built IPA is available and signed.
