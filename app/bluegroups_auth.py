import requests
import xmltodict
import logging

logger = logging.getLogger(__name__)

def is_user_in_group(email: str, group_name: str) -> bool:
    """
    Check if an IBM user belongs to a given BlueGroup.
    Returns True if rc=0 (user in group).
    """
    url = f"https://bluepages.ibm.com/tools/groups/groupsxml.wss?task=inAGroup&email={email}&group={group_name}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = xmltodict.parse(response.text)
        rc_value = data.get("group", {}).get("rc")
        in_group = rc_value == "0"
        logger.info(f"[BlueGroups] {email} in '{group_name}': {in_group}")
        return in_group
    except Exception as e:
        logger.error(f"Error checking BlueGroup membership for {email}: {e}")
        return False