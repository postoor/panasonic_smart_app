# panasonic_smart_app

Home Assistant custom component for Panasonic Smart App (Taiwan, ems2.panasonic.com.tw).
Integration code lives in `custom_components/panasonic_smart_app/`.

## Test

The project `.venv` is broken (its interpreter symlinks point at a removed
miniforge). Use the working 3.12 interpreter with the venv's site-packages:

```
SP="$(pwd)/.venv/lib/python3.12/site-packages"
PYTHONPATH="$SP" /home/lksdub/.local/bin/python3.12 -m unittest discover -s tests
```

`homeassistant` 2025.1.4 is installed in that site-packages, so `sensor.py`
etc. can be imported as a package via `tests/` (see `tests/test_dryer.py`).

## Build / Run

No build step. It is installed into a Home Assistant instance (HACS or by
copying `custom_components/panasonic_smart_app/`). No runnable app in this repo.

## Probe the real account

`.env` holds `USERNAME` / `PASSWORD`. A standalone script can drive the API via
`from smartApp import SmartApp` (`login()`, `get_devices()`, `get_commands()`,
`get_device_info(auth, gwid, codes)`). aiohttp's default aiodns resolver is
incompatible here — pass `aiohttp.TCPConnector(resolver=aiohttp.ThreadedResolver())`.

## Device model

`DEVICE_STATUS_CODES` in `const.py` maps `DeviceType` -> status codes the
coordinator fetches; platforms branch on `int(device["DeviceType"])`. Sensors
decode a status code's value by matching it against that model's `Parameters`
list from the API command list (`self.commands`).

## Lessons

- 2026-11-24: Clothes dryer (烘衣機) is DeviceType 6 (ModelType CN-HP, e.g.
  NH-VS100HP), distinct from washing machine DeviceType 3. Dryer remaining time
  is status 0x05 (washer uses 0x13); 0x50 status / 0x55 cycle are shared.
