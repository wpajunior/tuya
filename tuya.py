import dotenv
import logging
import os
import socket
import time
import tinytuya


dotenv.load_dotenv()

MINI_PC_IP = os.environ.get("MINI_PC_IP")
MINI_PC_SSH_PORT = os.environ.get("MINI_PC_SSH_PORT", 22)
MINI_PC_OUTLET_IP = os.environ.get("MINI_PC_OUTLET_IP")
OUTLET_DEVICE_ID = os.environ.get("OUTLET_DEVICE_ID")
OUTLET_LOCAL_KEY = os.environ.get("OUTLET_LOCAL_KEY")
MAX_COUNTER = 3


def get_outlet_device():
    d = tinytuya.OutletDevice(
        dev_id=OUTLET_DEVICE_ID,
        address=MINI_PC_OUTLET_IP,
        local_key=OUTLET_LOCAL_KEY,
    )
    d.set_version(3.3)
    return d


def is_port_open(host, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(1)
    try:
        s.connect((host, port))
        s.close()
        return True
    except (socket.timeout, ConnectionRefusedError):
        return False


def is_outlet_on(d):
    status = d.status()
    # dps "1" is typically the main switch for OutletDevice
    return status.get("dps", {}).get("1", False)


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[logging.StreamHandler()],
    )

    d = get_outlet_device()

    for i in range(MAX_COUNTER):
        if is_port_open(MINI_PC_IP, int(MINI_PC_SSH_PORT)):
            logging.info("Mini PC is reachable. No action needed.")
            return
        elif not is_outlet_on(d):
            logging.info(f"The outlet is currently OFF. No action needed.")
            return
        else:
            logging.info(f"Mini PC unreacheable. Counter: {i}")
            time.sleep(20)

    d.turn_off(1, True)
    logging.info("Mini PC turned off.")


if __name__ == "__main__":
    main()
