"""Tests for podcast server — verify import, fetcher, pipeline, protocol."""

def test_fetcher_import():
    from servers.podcast.fetcher import parse_episode_id, fetch_episode_detail
    assert callable(parse_episode_id)
    assert callable(fetch_episode_detail)

def test_parse_episode_id():
    from servers.podcast.fetcher import parse_episode_id
    assert parse_episode_id("https://www.xiaoyuzhoufm.com/episode/abc123") == "abc123"
    assert parse_episode_id("https://www.xiaoyuzhoufm.com/episode/6a0c7467e1eb34a939b604ad") == "6a0c7467e1eb34a939b604ad"

def test_pipeline_import():
    from servers.podcast.pipeline import analyze_episode
    assert callable(analyze_episode)

def test_server_import():
    import servers.podcast.server
    assert True
