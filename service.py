import threading
import json
import binascii
import xbmc
import xbmcvfs
import requests

from urllib.parse import urlparse

DEFAULT_SERVER = ""
DEFAULT_APIKEY = ""

class UpNextJfMonitor(xbmc.Monitor):
    cached_jf_servers = {}

    def __init__(self):
        super().__init__()
        self.timer_upnext = None

    def __del__(self):
        self.timer_upnext_stop()

    @staticmethod
    def upnext_data_event(data):
        data = binascii.hexlify(json.dumps(data).encode("utf-8")).decode("utf-8")
        data = '"[%s]"' % json.dumps(data).replace('"', '\\"')
        xbmc.executebuiltin("NotifyAll(plugin.video.jellyfin, upnext_data, %s)" % data)

    @staticmethod
    def get_intro_skipper_credits_offset(next_info, base_url, api_key):
        intro_skipper_credits_data = requests.get(
            f"{base_url}/Episode/{next_info['current_episode']['episodeid']}/IntroTimestamps/v1",
            params={
                "mode": "Credits",
            },
            headers={
                "Accept": "application/json",
                "Accept-Charset": "UTF-8,*",
                "Authorization": f"MediaBrowser Token={api_key}",
            },
            timeout=5
        )
        intro_skipper_credits_data.raise_for_status()
        intro_skipper_credits_data = intro_skipper_credits_data.json()

        if intro_skipper_credits_data["Valid"]:
            return intro_skipper_credits_data["ShowSkipPromptAt"]

    @staticmethod
    def get_server_and_api_key(next_info):
        try:
            if not UpNextJfMonitor.cached_jf_servers:
                with open(xbmcvfs.translatePath("special://profile/addon_data/plugin.video.jellyfin/data.json"), "rb") as f:
                    data = json.load(f)

                for i in data["Servers"]:
                    try:
                        UpNextJfMonitor.cached_jf_servers[i["address"]] = i["AccessToken"]
                    except Exception:
                        continue

            for value in next_info["current_episode"]["art"].values():
                try:
                    parsed_url = urlparse(value)
                    base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
                    return base_url, UpNextJfMonitor.cached_jf_servers[base_url]
                except Exception:
                    continue
        except Exception:
            pass

        return DEFAULT_SERVER, DEFAULT_APIKEY

    def timer_upnext_cb(self, next_info, timer_id, playing_file):
        try:
            base_url, api_key = UpNextJfMonitor.get_server_and_api_key(next_info)
            if not base_url or not api_key:
                return
            if not (notification_offset := UpNextJfMonitor.get_intro_skipper_credits_offset(next_info, base_url, api_key)):
                return
            next_info["notification_offset"] = notification_offset

            if id(self.timer_upnext) != timer_id:
                return

            player = xbmc.Player()
            if not player.isPlayingVideo():
                return
            now_playing_file = player.getPlayingFile()
            if (not now_playing_file) or (playing_file and now_playing_file != playing_file):
                return

            UpNextJfMonitor.upnext_data_event(next_info)
        except Exception:
            return
        finally:
            self.timer_upnext = None

    def timer_upnext_stop(self):
        if self.timer_upnext is None:
            return
        self.timer_upnext.cancel()
        self.timer_upnext = None

    def onNotification(self, sender, method, data):
        if not data or method != "Other.upnext_data" or sender != "plugin.video.jellyfin":
            return

        next_info = json.loads(binascii.unhexlify(json.loads(data)[0]))
        if "notification_offset" in next_info or "notification_time" in next_info:
            return

        self.timer_upnext_stop()
        self.timer_upnext = threading.Timer(10.0, self.timer_upnext_cb)
        self.timer_upnext.args = (next_info, id(self.timer_upnext), xbmc.Player().getPlayingFile())
        self.timer_upnext.start()


if __name__ == "__main__":
    monitor = UpNextJfMonitor()
    monitor.waitForAbort()

    del monitor
