# Trigger ZoneMinder alarms
[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration) ![hacs_validation](https://github.com/hbrennhaeuser/homeassistant_integration_zmtrigger/actions/workflows/hacs_validation.yml/badge.svg?branch=main) ![validate_with_hassfest](https://github.com/hbrennhaeuser/homeassistant_integration_zmtrigger/actions/workflows/validate_with_hassfest.yml/badge.svg?branch=main)
This custom component allows you to trigger an ZoneMinder alarm.

This component is best used to trigger an alarm for X seconds (e.g. on+10).
If you want to switch an alarm on and off, I recommend you take a look at this [gist](https://gist.github.com/hbrennhaeuser/383c515b44771950f920eb62c76831c2) using the official telnet integration.

Using this over the telnet-integration has the additional advantage that you can easily change the parameters like the monitorid on the fly, instead of having to create multiple switches for every camera and trigger combination.

## Installation

The recommended way to install this integration is through HACS.

### HACS

Add this repository as a custom repository in hacs (category: integration).
When the custom repository is added you can search for and install this integration.

Make sure to restart Home Assistant after the installation.

### Manual

Copy custom_components/zmtrigger to config/custom_components/zmtrigger.

Make sure to restart Home Assistant after the installation.

## Configuration

Make sure OPT_TRIGGERS are enabled in ZoneMinder!

Define a new zmtrigger notification-service in configuration.yaml:

```yaml
notify:
    - name: zmtrigger
      platform: zmtrigger
      host: zonerminder.domain.tld  # ZoneMinder host
      port: 6802  # telnet port, optional, default: 6802
      timeout: 10  # telnet timeout in seconds, optional default: 2
```

Optionally you can set default values for the optional parameters. They may be overridden in the notification-call:

```yaml
      monitorid: 31  # No default value
      action: 'on+10'  # Default: on+5
      score: 100  # Default: 1
      cause: 'HomeAssistant'  # Default: HAtrigger
```

Have a look at the zmtrigger.pl-manpage or the pod at the end of [zmtrigger.pl](https://github.com/ZoneMinder/ZoneMinder/blob/master/scripts/zmtrigger.pl.in) for more details on the parameters.


## Usage

Call the notification service anywhere in Home Assistant:

```yaml
service: notify.zmtrigger
data:
  message: Doorbell  # zmtrigger->text
  data: 
    monitorid: 31  # only required if you did not set a default value in configuration.yaml
```

Optionally define additional data.

```yaml
service: notify.zmtrigger
data:
  message: Doorbell  # zmtrigger->text
  data:
    monitorid: 31
    action: 'on+35'
    score: 100
    cause: 'HA'
    showtext: 'Doorbell'
    
```
