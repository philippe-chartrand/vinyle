def define_subtitle(song, artist_to_highlight=None, delim="\r"):
    artist_subtitle = ", ".join(artist for artist in song["artist"])
    composer_subtitle = ", ".join(composer for composer in song["composer"])
    conductor_subtitle = ", ".join(conductor for conductor in song["conductor"])
    credits = []
    found_in_credits = False
    if artist_subtitle:
        credits.append(artist_subtitle)
    if composer_subtitle:
        credits.append(composer_subtitle)
    if conductor_subtitle:
        credits.append(conductor_subtitle)
    if subtitle := delim.join(credits):
        if artist_to_highlight in credits:
            found_in_credits = True
        return subtitle, found_in_credits