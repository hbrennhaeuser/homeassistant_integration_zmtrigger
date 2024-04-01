"""zmtrigger notification service."""
import logging
from homeassistant.components.notify import (
    ATTR_MESSAGE,
    ATTR_TITLE,
    ATTR_TITLE_DEFAULT,
    ATTR_DATA,
    PLATFORM_SCHEMA,
    BaseNotificationService,
)
import homeassistant.helpers.config_validation as cv

import voluptuous as vol
import telnetlib
import re


from homeassistant.const import (
    CONF_HOST,
    CONF_PORT,
    CONF_TIMEOUT,
)

from .const import (
    CONF_MONITORID,
    CONF_ACTION,
    CONF_SCORE,
    CONF_CAUSE,
    DEFAULT_PORT,
    DEFAULT_TIMEOUT,
    DEFAULT_ACTION,
    DEFAULT_SCORE,
    DEFAULT_CAUSE
)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_HOST): cv.string,
        vol.Optional(CONF_PORT, default=DEFAULT_PORT): cv.string,
        vol.Optional(CONF_TIMEOUT, default=DEFAULT_TIMEOUT): vol.Coerce(float),
        vol.Optional(CONF_MONITORID): vol.Coerce(int),
        vol.Optional(CONF_ACTION, default=DEFAULT_ACTION): cv.string,
        vol.Optional(CONF_SCORE, default=DEFAULT_SCORE): vol.Coerce(int),
        vol.Optional(CONF_CAUSE, default=DEFAULT_CAUSE): cv.string,
    }
)

_LOGGER = logging.getLogger(__name__)


def get_service(hass,config, discovery_info=None):
    return ZmtriggerNotificationService(config)



class ZmtriggerNotificationService(BaseNotificationService):
    def __init__ (self, config):
        """Initialize the zmtrigger notification service"""
        if config.get(CONF_HOST) is None:
            raise ValueError("No host specified!")

        self.host = config.get(CONF_HOST)
        self.port = config.get(CONF_PORT)
        self.timeout = config.get(CONF_TIMEOUT)

        self.monitorid = config.get(CONF_MONITORID)
        self.action = config.get(CONF_ACTION)
        self.score = config.get(CONF_SCORE)
        self.cause = config.get(CONF_CAUSE)

    def _telnet_command(self, command: str) -> str | None:
        try:
            telnet = telnetlib.Telnet(self.host, self.port)
            telnet.write(command.encode("ASCII") + b"\r")
            response = telnet.read_until(b"\r", timeout=self.timeout)
        except Exception as e:
            _LOGGER.error(
                'Command "%s" failed with exception: %s', command, repr(e)
            )
            return None
        _LOGGER.debug("telnet response: %s", response.decode("ASCII").strip())
        return response.decode("ASCII").strip()


    def send_message(self, message="", **kwargs):
        """Execute zmtrigger"""
        data=kwargs.get(ATTR_DATA,[])

        # --
        monitorid = self.monitorid
        action = self.action
        score = self.score
        cause = self.cause
        text = None
        showtext = None
        
        # Override parameters if specified
        if "monitorid" in data:
            monitorid = data["monitorid"]

        if "action" in data:
            action = data["action"]

        if "score" in data:
            score = data["score"]

        if "cause" in data:
            cause = str(data["cause"])

        text = str(message)

        if "showtext" in data:
            showtext = str(data["showtext"])

        # Check required parameters
        if monitorid is None:
            raise SyntaxError('monitorid is required!')
    
        if not isinstance(monitorid, int):
            raise ValueError('monitorid is not an integer')

        if action is None:
            raise SyntaxError('Action is required!')

        if not re.match(r'^((on|off)(\+[0-9]+)?)|(cancel|show)$', action):
            raise ValueError('Invalid action specified!')

        if score is None:
            raise SyntaxError('Score is required!')
        
        if not isinstance(score, int):
            raise ValueError('monitorid is not an integer')

        if score < 0 or score > 100:
            raise ValueError('Invalid score specified! Out of range 0:100')

        if cause is None:
            raise SyntaxError('Cause is required!')

        if text is None:
            raise SyntaxError('text (message) is required!')

        # Ensure max character length
        cause = cause [:32]

        if showtext is not None:
            showtext = showtext [:32]

        text = text [:256]

        # Send trigger
        # id|action|score|cause|text|showtext
        command=f"{monitorid}|{action}|{score}|{cause}|{text}"

        if showtext is not None:
            command+=f"|{showtext}"

        _LOGGER.debug("Assembled command %s", command)

        self._telnet_command(command)