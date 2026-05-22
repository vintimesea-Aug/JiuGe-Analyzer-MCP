"""Tests for podcast server — verify import, schema, pipeline, protocol."""

def test_fetcher_import():
    from servers.podcast.fetcher import parse_episode_id, fetch_episode_detail
    assert callable(parse_episode_id)
    assert callable(fetch_episode_detail)

def test_parse_episode_id():
    from servers.podcast.fetcher import parse_episode_id
    assert parse_episode_id("https://www.xiaoyuzhoufm.com/episode/abc123") == "abc123"
    assert parse_episode_id("https://www.xiaoyuzhoufm.com/episode/6a0c7467e1eb34a939b604ad") == "6a0c7467e1eb34a939b604ad"

def test_schema_imports():
    from core.schema import (
        SCHEMA_VERSION, FAST_REQUIRED, DEEP_REQUIRED,
        build_fast_system, build_fast_user,
        build_deep_system, validate,
    )
    assert SCHEMA_VERSION >= 1
    assert len(FAST_REQUIRED) >= 5
    assert len(DEEP_REQUIRED) >= 5

def test_validate_good():
    from core.schema import validate, FAST_REQUIRED
    analysis = {
        "overview": {"summary": "this is a detailed overview that has more than five words", "stance": "neutral", "knowledge_density": "high"},
        "topic_classification": {"primary_field": "tech", "cross_disciplines": ["economics", "sociology"]},
        "core_arguments": ["point one with enough words to pass the five word threshold", "point two with enough words to pass the five word threshold"],
        "extended_thinking": "this is a long enough string that has many words and will definitely pass the five word minimum easily",
        "audience_guide": {"who_should_listen": ["tech enthusiasts", "business students"], "prerequisites": ["basic economics"], "best_scenarios": ["commute listening", "morning routine"]},
        "overall_rating": {
            "recommendation": "⭐⭐⭐⭐",
            "dimensions": {"info_density": 4, "argument_quality": 4, "knowledge_gain": 3, "brilliance": 4},
            "weaknesses": "knowledge_gain could be deeper",
        },
    }
    assert validate(analysis, FAST_REQUIRED) == []

def test_validate_missing():
    from core.schema import validate, FAST_REQUIRED
    assert len(validate({}, FAST_REQUIRED)) >= 5

def test_validate_null():
    from core.schema import validate, FAST_REQUIRED
    assert len(validate({"overview": None, "topic_classification": {}, "core_arguments": [], "extended_thinking": "", "audience_guide": {}, "overall_rating": {}}, FAST_REQUIRED)) > 0

def test_pipeline_import():
    from servers.podcast.pipeline import analyze_episode, analyze_episode_deep
    assert callable(analyze_episode)
    assert callable(analyze_episode_deep)

def test_server_import():
    import servers.podcast.server
    assert True
