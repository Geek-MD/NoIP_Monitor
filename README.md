[![Geek-MD - NoIP Monitor](https://img.shields.io/static/v1?label=Geek-MD&message=NoIP%20Monitor&color=blue&logo=github)](https://github.com/Geek-MD/NoIP_Monitor)
[![Stars](https://img.shields.io/github/stars/Geek-MD/NoIP_Monitor?style=social)](https://github.com/Geek-MD/NoIP_Monitor)
[![Forks](https://img.shields.io/github/forks/Geek-MD/NoIP_Monitor?style=social)](https://github.com/Geek-MD/NoIP_Monitor)

[![GitHub Release](https://img.shields.io/github/release/Geek-MD/NoIP_Monitor?include_prereleases&sort=semver&color=blue)](https://github.com/Geek-MD/NoIP_Monitor/releases)
[![License](https://img.shields.io/badge/License-MIT-blue)](https://github.com/Geek-MD/NoIP_Monitor/blob/main/LICENSE)
[![HACS Custom Repository](https://img.shields.io/badge/HACS-Custom%20Repository-blue)](https://hacs.xyz/)

[![Ruff + Mypy + Hassfest](https://github.com/Geek-MD/NoIP_Monitor/actions/workflows/validate.yaml/badge.svg)](https://github.com/Geek-MD/NoIP_Monitor/actions/workflows/validate.yaml)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Checked with mypy](https://www.mypy-lang.org/static/mypy_badge.svg)](https://mypy-lang.org/)

<img width="200" height="200" alt="icon" src="https://github.com/Geek-MD/NoIP_Monitor/blob/main/icon.png?raw=true" />

# NoIP Monitor

A custom Home Assistant integration to monitor your NoIP dynamic hostnames' IP addresses.

---

## ✨ Features

- ✅ Full UI configuration
- ✅ Configuration editing from UI
- ✅ Support for multiple hostnames/groups
- ✅ Each hostname created as an independent sensor
- ✅ "Disconnected" state when IP is unavailable
- ✅ Automatic updates every 5 minutes
- ✅ Dynamic icons (connected/disconnected)
- ✅ Additional attributes with status information
- ✅ Spanish and English localization

---

## 📦 Installation

### Option 1: Installation via HACS (Recommended)

1. Open HACS in your Home Assistant
2. Go to "Integrations"
3. Click the three-dot menu (top right)
4. Select "Custom repositories"
5. Add URL: `https://github.com/Geek-MD/NoIP_Monitor`
6. Select category: "Integration"
7. Search for "NoIP Monitor" and click "Download"
8. Restart Home Assistant

### Option 2: Manual Installation

1. Copy the `custom_components/noip_monitor` folder to your `config/custom_components/` directory
2. Restart Home Assistant

---

## ⚙️ Configuration

### Initial Setup

1. Go to **Settings** → **Devices & Services**
2. Click **+ Add Integration**
3. Search for **NoIP Monitor**
4. Enter your NoIP credentials:
   - **Username**: Your NoIP username
   - **Password**: Your NoIP password
5. Click **Submit**

### Configure Hostnames

1. Go to **Settings** → **Devices & Services**
2. Find **NoIP Monitor** in the list
3. Click **Configure** (gear icon)
4. Enter the hostnames you want to monitor, comma-separated:
   - Example: `myhost.ddns.net, server.hopto.org`
   - Leave empty to monitor all hostnames in your account
5. Click **Submit**

---

## 📊 Sensors

Each configured hostname creates an independent sensor with:

- **State**: The current dynamic IP or "Disconnected"
- **Icon**: 
  - 🌐 `mdi:lan-connect` when connected
  - 🔌 `mdi:lan-disconnect` when disconnected

### Attributes

- `hostname`: The configured NoIP hostname
- `status`: Connection status (`connected` / `disconnected`)
- `response`: NoIP API response (`good` / `nochg`)
- `error`: Error message if there's any issue

---

## 📝 Examples

### Notification Automation

```yaml
automation:
  - alias: "Notify NoIP IP Change"
    trigger:
      - platform: state
        entity_id: sensor.myhost_ddns_net
    action:
      - service: notify.mobile_app
        data:
          title: "NoIP IP Change"
          message: "New IP: {{ states('sensor.myhost_ddns_net') }}"
```

### Dashboard Card

```yaml
type: entities
title: NoIP Monitor
entities:
  - entity: sensor.myhost_ddns_net
  - entity: sensor.server_hopto_org
show_header_toggle: false
```

### Card with Attributes

```yaml
type: markdown
content: |
  ## NoIP Status
  
  **Hostname:** {{ state_attr('sensor.myhost_ddns_net', 'hostname') }}
  **IP:** {{ states('sensor.myhost_ddns_net') }}
  **Status:** {{ state_attr('sensor.myhost_ddns_net', 'status') }}
```

---

## 🔧 Troubleshooting

**Issue: Sensor shows "Disconnected"**
- Verify your NoIP credentials are correct
- Make sure the hostname exists in your NoIP account
- Check Home Assistant logs for more details

**Issue: No sensors appear**
- Configure hostnames in the integration options
- Restart Home Assistant after configuration

**Issue: Authentication error**
- Verify your NoIP username and password
- Make sure you don't have special characters that might cause issues

---

## 🐛 Report Issues

If you find any issues or have suggestions, please open an issue at:

https://github.com/Geek-MD/NoIP_Monitor/issues

---

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- Home Assistant Community
- NoIP for their Dynamic DNS service

---

## 📌 Version

**v0.1.0** - Initial release

---

<div align="center">
  
💻 **Proudly developed with GitHub Copilot** 🚀

</div>
