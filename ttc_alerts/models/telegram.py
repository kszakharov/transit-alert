"""
Telegram notification models
"""

from dataclasses import dataclass
from typing import List, Self
from datetime import datetime
import jinja2
import re

from .alert import TTCAlert


MESSAJE_TEMPLATE = """
{% if new_alerts %}
🚨 <b>NEW TTC SERVICE ALERTS</b> 🚨
━━━━━━━━━━━━━━━
{% for alert in new_alerts %}
{% if 'Line' in alert.header %}
🚇 <b>{{ alert.header }}</b>
{% elif 'Bus' in alert.header or alert.header | regex_match('^\d+') %}
🚌 <b>{{ alert.header }}</b>
{% else %}
⚠️ <b>{{ alert.header }}</b>
{% endif %}
📋 {{ alert.description }}
{% if not loop.last %}
━━━━━━━━━━━━━━━
{% endif %}
{% endfor %}
{% endif %}
{% if resolved_alerts %}
✅ <b>RESOLVED TTC ALERTS</b> ✅
━━━━━━━━━━━━━━━
{% for alert in resolved_alerts %}
{% if 'Line' in alert.header %}
🚇 <s>{{ alert.header }}</s> ✅
{% elif 'Bus' in alert.header or alert.header | regex_match('^\d+') %}
🚌 <s>{{ alert.header }}</s> ✅
{% else %}
⚠️ <s>{{ alert.header }}</s> ✅
{% endif %}
📋 <i>{{ alert.description }}</i>
{% if not loop.last %}
━━━━━━━━━━━━━━━
{% endif %}
{% endfor %}
{% endif %}
{% if not new_alerts and not resolved_alerts %}
🎉 <b>ALL CLEAR</b> 🎉
━━━━━━━━━━━━━━━
✨ No active TTC service alerts at this time!
🚇🚌 All services running normally.
{% endif %}
───────────────
🤖 <i>TTC Alert Bot | Stay informed, travel smart</i>
"""

@dataclass
class TelegramMessage:
    """Telegram message model"""
    text: str
    parse_mode: str = "HTML"
    
    @classmethod
    def from_alerts(cls, alert_type: str, alerts: List[TTCAlert]) -> Self:
        """
        Create a message from a list of alerts
        
        Args:
            alert_type: Type of alert change ("new", "resolved", or "unresolved")
            alerts: List of alerts to include in the message
        """
        if not alerts:
            return None
            
        # Create template environment
        env = jinja2.Environment()
        env.filters['regex_match'] = lambda text, pattern: bool(re.match(pattern, text))
        env.filters['strftime'] = lambda dt, fmt: dt.strftime(fmt)
        
        template = env.from_string(MESSAJE_TEMPLATE)
        
        # Prepare template data
        template_data = {
            'new_alerts': alerts if alert_type == 'new' else [],
            'resolved_alerts': alerts if alert_type == 'resolved' else [],
            'timestamp': datetime.now()
        }
        
        # Render template
        message = template.render(**template_data)

        message = re.sub(r'\n\s*\n+', '\n', message).strip()
            
        return cls(text=message) 