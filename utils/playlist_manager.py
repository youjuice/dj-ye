class PlaylistManager:
    def __init__(self):
        self.playlist = []
        self.current_index = -1

    def add_song(self, song):
        self.playlist.append(song)
        if self.current_index == -1:
            self.current_index = 0

    def get_next_song(self):
        if not self.playlist:
            return None
        self.current_index = (self.current_index + 1) % len(self.playlist)
        return self.playlist[self.current_index]

    def get_previous_song(self):
        if not self.playlist:
            return None
        self.current_index = (self.current_index - 1) % len(self.playlist)
        return self.playlist[self.current_index]

    def move_to_next_song(self):
        if self.playlist:
            self.current_index = (self.current_index + 1) % len(self.playlist)

    def move_to_prev_song(self):
        if self.playlist:
            self.current_index = (self.current_index - 1) % len(self.playlist)

    def get_current_song(self):
        if not self.playlist or self.current_index == -1:
            return None
        return self.playlist[self.current_index]

    def clear_playlist(self):
        self.playlist = []
        self.current_index = -1

    def get_playlist(self):
        return self.playlist
