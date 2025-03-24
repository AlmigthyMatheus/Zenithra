```md
# Zenithra - Discord Music Bot with Spotify Integration

**Zenithra** is a feature-rich Discord music bot that integrates with the Spotify API and streams music via YouTube. Built with Python and [discord.py](https://discordpy.readthedocs.io/), Zenithra allows users to search for, queue, and control music playback directly in Discord voice channels.

## Key Features

- **Music Playback:**  
  Use the command `!play [song name or URL]` to search for and play music from YouTube, YouTube Music, or Spotify. Spotify links are processed to fetch track details via the Spotify API and then converted into YouTube search queries.

- **Queue Management:**  
  Manage your music queue with commands such as:
  - `!skip` – Skip the current track.
  - `!stop` – Stop playback and clear the queue.
  - `!pause` – Pause the current track.
  - `!resume` – Resume a paused track.
  - `!queue` – Display the current music queue.
  - `!help` – Display the help message.

- **Spotify Integration:**  
  Retrieve track details (e.g., title and artist) from public Spotify playlists and individual tracks using [Spotipy](https://spotipy.readthedocs.io/) (Client Credentials Flow).

- **Cookie Support (Optional):**  
  If you encounter region-lock or restricted videos on YouTube, include a `cookies.txt` file (exported from your browser) in the project root. This allows yt-dlp to use your cookies for accessing the content.

## Requirements

- Python 3.8+
- [discord.py](https://discordpy.readthedocs.io/)
- [yt-dlp](https://github.com/yt-dlp/yt-dlp)
- [PyNaCl](https://pypi.org/project/PyNaCl/)
- [Spotipy](https://spotipy.readthedocs.io/)
- [FFmpeg](https://ffmpeg.org/)

## Setup and Installation

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/yourusername/Zenithra.git
   cd Zenithra
   ```

2. **Install Dependencies:**

   Use pip to install the required packages:

   ```bash
   pip install discord.py yt-dlp PyNaCl spotipy
   ```

3. **Configure Environment Variables:**

   Set the following environment variables using your preferred method (for example, using a `.env` file or Replit Secrets):
   - `DISCORD_TOKEN`: Your Discord bot token.
   - `SPOTIFY_CLIENT_ID`: Your Spotify Client ID.
   - `SPOTIFY_CLIENT_SECRET`: Your Spotify Client Secret.

4. **Using Cookies (Optional):**

   If you encounter issues with videos being unavailable, export your YouTube cookies (using an extension like [Get cookies.txt](https://chrome.google.com/webstore/detail/get-cookiestxt/lgplbmmbhfpjfbjgdkocpjnakobppfmo)) to a file named `cookies.txt` and place it in the root directory of the project.

5. **Replit Configuration (if applicable):**

   - **Secrets:**  
     Set `DISCORD_TOKEN`, `SPOTIFY_CLIENT_ID`, and `SPOTIFY_CLIENT_SECRET` in the Replit Secrets panel.
   - **replit.nix:**  
     Create or edit the `replit.nix` file in the project root to include FFmpeg:
     ```nix
     { pkgs }: {
       deps = [
         pkgs.ffmpeg
         pkgs.python39Full
       ];
     }
     ```

6. **Test on Replit:**

   You can test the bot on Replit via this link:  
   [replit.com/@patativagames/Zenihtra](https://replit.com/@patativagames/Zenihtra)

## Usage

Run the bot with:

```bash
python main.py
```

Once running, invite the bot to your Discord server using the OAuth2 URL from the Discord Developer Portal. In your server, use commands such as:

- `!play [song name or URL]` – Plays the specified song or playlist.
- `!skip` – Skips the current track.
- `!pause` – Pauses the current track.
- `!resume` – Resumes the paused track.
- `!stop` – Stops playback and clears the queue.
- `!queue` – Displays the current music queue.
- `!help` – Shows this help message.

## Troubleshooting

- **Spotify API Errors:**  
  Ensure the playlist or track is public. The Client Credentials Flow only grants access to public data. Verify that `SPOTIFY_CLIENT_ID` and `SPOTIFY_CLIENT_SECRET` are set correctly.

- **YouTube "Video unavailable" Errors:**  
  Some videos may be restricted by region or DRM. Using a `cookies.txt` file can help if those videos are available when logged in. For YouTube Music playlists, the bot automatically converts the link to a standard YouTube playlist.

- **FFmpeg Warnings:**  
  Warnings about options (e.g., bitrate) are informational and can generally be ignored.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

Feel free to open issues or submit pull requests with suggestions for improvements!
