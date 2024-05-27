Hack to get [MoojMidge's fork of the UpNext Kodi plugin](https://github.com/MoojMidge/service.upnext) to use the detected credit time of a video from [jumoog's fork of the Intro Skipper Jellyfin plugin](https://github.com/jumoog/intro-skipper).

In Kodi, you need MoojMidge's UpNext fork installed, and [Jellyfin for Kodi](https://jellyfin.org/docs/general/clients/kodi/#jellyfin-for-kodi) installed - *not* JellyCon.
On your Jellyfin server, you need jumoog's Intro Skipper fork installed - make sure it's configured to detect credits.

This hack works by listening for the UpNext notification the Jellyfin Kodi plugin sends out, adding the credit time offset from the Intro Skipper plugin and sending a new notification to the UpNext plugin. As the UpNext plugin doesn't appear to handle notifications for the same video sent too closely, this waits 10 seconds before doing so.

This plugin tries to get the address for the right Jellyfin server automatically, but it's not really a reliable check. As the Intro Skipper plugin requires authentication to call its API methods, the plugin tries to use the Jellyfin plugin's stored API key.

Quick instructions:

1. Download this repository as a ZIP

2. It's recommended to add a fallback server and API key to service.py

3. Install the ZIP file in Kodi

4. Restart Kodi to make sure the service is started

Q: Why this hack instead of modifying the Jellyfin for Kodi or UpNext plugin?

I don't want to fork either. Being an official product from the Jellyfin organisation, I can't see the Jellyfin for Kodi maintainers adding support for a third-party Jellyfin plugin in their code; I also can't see the UpNext developers adding functionality for a specific addon to their code, either.