import random


class PlaylistManager:
    def __init__(self):
        self.playlist = []
        self.current_index = -1

    def add_song(self, song):
        self.playlist.append(song)
        if self.current_index == -1:
            self.current_index = 0

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

    def remove_song(self, index):
        if 0 <= index < len(self.playlist):
            removed_song = self.playlist.pop(index)
            if index < self.current_index:
                self.current_index -= 1
            elif index == self.current_index:
                self.current_index = min(self.current_index, len(self.playlist) - 1)
            return removed_song
        return None

    def jump_to_song(self, index):
        if 0 <= index < len(self.playlist):
            self.current_index = index
            return self.playlist[self.current_index]
        return None

    def shuffle_playlist(self):
        current_song = self.playlist[self.current_index] if self.current_index != -1 else None
        random.shuffle(self.playlist)
        if current_song:
            self.current_index = self.playlist.index(current_song)
        else:
            self.current_index = -1
