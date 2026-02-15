from ai_aimbot.config import ProfileLoader, list_profiles


def test_builtin_profiles_load():
    for _, path in list_profiles().items():
        profile = ProfileLoader.load(path)
        assert profile.name
        assert profile.model_path.endswith('.pt')
        assert profile.aim.fov_radius > 0
