import nfc
import ndef
import threading
import logging

# Set up basic logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger('nfcemu')

class NFC_Emulator:
    def __init__(self, device='tty:AMA0:pn532'):
        self.clf = nfc.ContactlessFrontend(device)
        if not self.clf:
            raise RuntimeError("Failed to open NFC device")

    def emulate_tag(self, ndef_message):
        """ Emulates an NFC tag with the given NDEF message. """
        try:
            log.info("Starting NFC tag emulation")
            self.clf.connect(rdwr={'on-connect': lambda tag: False, 'on-release': lambda tag: False})
            # Setup the target settings for emulation
            target = nfc.clf.RemoteTarget("106A")  # Type 2 Tag emulation
            target.sens_res = bytearray.fromhex("0004")  # SENS_RES response
            target.sel_res = 0x20  # SEL_RES response
            target.ndef = ndef_message

            # Start the tag emulation
            self.clf.emulate_target(target)
        except Exception as e:
            log.error(f"An error occurred during NFC emulation: {e}")
        finally:
            self.clf.close()

    def create_ndef_message(self, url):
        """ Creates an NDEF message containing a URL record. """
        record = ndef.UriRecord(url)
        return [record]

    def start_emulation(self, url):
        """ Prepares and starts NFC tag emulation with a URL. """
        ndef_message = self.create_ndef_message(url)
        self.emulate_tag(ndef_message)

# Usage
if __name__ == "__main__":
    emulator = NFC_Emulator()
    emulator.start_emulation("https://github.com")
