from three_circles_chords.scenes import OPTION_LETTERS, OPTION_SCENES, export_basename, scene_for


def test_four_option_scenes_defined():
    assert set(OPTION_SCENES) == set(OPTION_LETTERS)


def test_export_basenames_unique():
    names = [export_basename(letter) for letter in OPTION_LETTERS]
    assert len(names) == len(set(names))


def test_scene_summaries_non_empty():
    for letter in OPTION_LETTERS:
        scene = scene_for(letter)
        assert scene.letter == letter
        assert scene.summary
        assert scene.strategy
