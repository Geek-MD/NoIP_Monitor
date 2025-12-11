# NoIP Monitor - Home Assistant Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)
[![Version](https://img.shields.io/badge/version-0.1.0-blue.svg)](https://github.com/Geek-MD/NoIP_Monitor)

Una integración personalizada de Home Assistant para monitorear las IPs dinámicas de tus hostnames de NoIP.

A custom Home Assistant integration to monitor your NoIP dynamic hostnames' IP addresses.

## 🌟 Características / Features

### Español
- ✅ Configuración completa a través de la interfaz de usuario (UI)
- ✅ Edición de la configuración desde la UI
- ✅ Soporte para múltiples hostnames/grupos
- ✅ Cada hostname se crea como un sensor independiente
- ✅ Estado "Disconnected" cuando la IP no está disponible
- ✅ Actualización automática cada 5 minutos
- ✅ Iconos dinámicos (conectado/desconectado)
- ✅ Atributos adicionales con información del estado

### English
- ✅ Full UI configuration
- ✅ Configuration editing from UI
- ✅ Support for multiple hostnames/groups
- ✅ Each hostname created as an independent sensor
- ✅ "Disconnected" state when IP is unavailable
- ✅ Automatic updates every 5 minutes
- ✅ Dynamic icons (connected/disconnected)
- ✅ Additional attributes with status information

## 📦 Instalación / Installation

### Vía HACS (Recomendado / Recommended)

1. Abre HACS en tu Home Assistant
2. Ve a "Integraciones"
3. Haz clic en el menú de tres puntos (arriba a la derecha)
4. Selecciona "Repositorios personalizados"
5. Añade la URL: `https://github.com/Geek-MD/NoIP_Monitor`
6. Selecciona la categoría: "Integration"
7. Busca "NoIP Monitor" y haz clic en "Descargar"
8. Reinicia Home Assistant

---

1. Open HACS in your Home Assistant
2. Go to "Integrations"
3. Click the three-dot menu (top right)
4. Select "Custom repositories"
5. Add URL: `https://github.com/Geek-MD/NoIP_Monitor`
6. Select category: "Integration"
7. Search for "NoIP Monitor" and click "Download"
8. Restart Home Assistant

### Instalación Manual / Manual Installation

1. Copia la carpeta `custom_components/noip_monitor` a tu directorio `config/custom_components/`
2. Reinicia Home Assistant

---

1. Copy the `custom_components/noip_monitor` folder to your `config/custom_components/` directory
2. Restart Home Assistant

## ⚙️ Configuración / Configuration

### Español

#### Configuración Inicial

1. Ve a **Configuración** → **Dispositivos y Servicios**
2. Haz clic en **+ Añadir integración**
3. Busca **NoIP Monitor**
4. Introduce tus credenciales de NoIP:
   - **Usuario**: Tu nombre de usuario de NoIP
   - **Contraseña**: Tu contraseña de NoIP
5. Haz clic en **Enviar**

#### Configurar Hostnames

1. Ve a **Configuración** → **Dispositivos y Servicios**
2. Encuentra **NoIP Monitor** en la lista
3. Haz clic en **Configurar** (icono de engranaje)
4. Introduce los hostnames que quieres monitorear, separados por comas:
   - Ejemplo: `mihost.ddns.net, servidor.hopto.org`
   - Deja vacío para monitorear todos los hostnames de tu cuenta
5. Haz clic en **Enviar**

### English

#### Initial Setup

1. Go to **Settings** → **Devices & Services**
2. Click **+ Add Integration**
3. Search for **NoIP Monitor**
4. Enter your NoIP credentials:
   - **Username**: Your NoIP username
   - **Password**: Your NoIP password
5. Click **Submit**

#### Configure Hostnames

1. Go to **Settings** → **Devices & Services**
2. Find **NoIP Monitor** in the list
3. Click **Configure** (gear icon)
4. Enter the hostnames you want to monitor, comma-separated:
   - Example: `myhost.ddns.net, server.hopto.org`
   - Leave empty to monitor all hostnames in your account
5. Click **Submit**

## 📊 Sensores / Sensors

Cada hostname configurado crea un sensor independiente con:

Each configured hostname creates an independent sensor with:

- **Estado / State**: La IP dinámica actual o "Disconnected"
- **Icono / Icon**: 
  - 🌐 `mdi:lan-connect` cuando está conectado / when connected
  - 🔌 `mdi:lan-disconnect` cuando está desconectado / when disconnected

### Atributos / Attributes

- `hostname`: El hostname de NoIP configurado
- `status`: Estado de la conexión (`connected` / `disconnected`)
- `response`: Respuesta de la API de NoIP (`good` / `nochg`)
- `error`: Mensaje de error si hay algún problema

## 📝 Ejemplos / Examples

### Automatización de Notificación / Notification Automation

```yaml
automation:
  - alias: "Notificar cambio de IP en NoIP"
    trigger:
      - platform: state
        entity_id: sensor.mihost_ddns_net
    action:
      - service: notify.mobile_app
        data:
          title: "Cambio de IP NoIP"
          message: "Nueva IP: {{ states('sensor.mihost_ddns_net') }}"
```

### Tarjeta de Dashboard / Dashboard Card

```yaml
type: entities
title: NoIP Monitor
entities:
  - entity: sensor.mihost_ddns_net
  - entity: sensor.servidor_hopto_org
show_header_toggle: false
```

### Tarjeta con Atributos / Card with Attributes

```yaml
type: markdown
content: |
  ## NoIP Status
  
  **Hostname:** {{ state_attr('sensor.mihost_ddns_net', 'hostname') }}
  **IP:** {{ states('sensor.mihost_ddns_net') }}
  **Status:** {{ state_attr('sensor.mihost_ddns_net', 'status') }}
```

## 🔧 Solución de Problemas / Troubleshooting

### Español

**Problema: El sensor muestra "Disconnected"**
- Verifica que tus credenciales de NoIP sean correctas
- Asegúrate de que el hostname existe en tu cuenta de NoIP
- Revisa los logs de Home Assistant para más detalles

**Problema: No aparecen sensores**
- Configura los hostnames en las opciones de la integración
- Reinicia Home Assistant después de configurar

**Problema: Error de autenticación**
- Verifica tu usuario y contraseña de NoIP
- Asegúrate de no tener caracteres especiales que puedan causar problemas

### English

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

## 🐛 Reportar Problemas / Report Issues

Si encuentras algún problema o tienes sugerencias, por favor abre un issue en:

If you find any issues or have suggestions, please open an issue at:

https://github.com/Geek-MD/NoIP_Monitor/issues

## 📄 Licencia / License

Este proyecto está licenciado bajo la Licencia MIT. Ver el archivo [LICENSE](LICENSE) para más detalles.

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## 🙏 Agradecimientos / Acknowledgments

- Home Assistant Community
- NoIP for their Dynamic DNS service

## 📌 Versión / Version

**v0.1.0** - Primera versión / Initial release