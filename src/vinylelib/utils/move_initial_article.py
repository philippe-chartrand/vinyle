def move_initial_article(item):
    moveable_articles_4 = ('The ', 'Les ')
    moveable_articles_3 = ('An ', 'Le ', 'La ')
    if item[0:4] in moveable_articles_4:
        return f"{item[4:]}, {item[0:3]}"
    elif item[0:3] in moveable_articles_3:
        return f"{item[3:]}, {item[0:2]}"
    else:
        return item