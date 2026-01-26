import pytest
from slide_voice_app.tts.ssml import SSMLProcessor


@pytest.fixture
def processor():
    """Provides a fresh instance of SSMLProcessor for every test."""
    return SSMLProcessor()


@pytest.mark.parametrize(
    "input_text, expected",
    [
        # Period next to words ignored, around spaces processed
        ("Hello. .. .World", '<speak>Hello. <break time="2s"/> .World</speak>'),
        # Period start/end of string
        (".", '<speak><break time="1s"/></speak>'),
        # Period start/end of paragraph
        ("\n.\n", '<speak>\n<break time="1s"/>\n</speak>'),
        # Inner underscore ignored, outer underscores processed
        (
            "check _my_variable_ value",
            '<speak>check <emphasis level="strong">my_variable</emphasis> value</speak>',
        ),
        # Underscore start/end of string
        ("_hello_", '<speak><emphasis level="strong">hello</emphasis></speak>'),
        # Underscore start/end of paragraph
        ("\n_hello_\n", '<speak>\n<emphasis level="strong">hello</emphasis>\n</speak>'),
        # Voice start of string
        (
            "[en-US-Wavenet-D]Hello there.",
            '<speak><voice name="en-US-Wavenet-D">Hello there.</voice></speak>',
        ),
        # Voice new paragraph
        (
            "Intro\n[en-US-Wavenet-D]Hello there.\n",
            '<speak>Intro\n<voice name="en-US-Wavenet-D">Hello there.</voice>\n</speak>',
        ),
        # Combined
        (
            "[en-US-Wavenet-D]Hi _there_ .. now",
            '<speak><voice name="en-US-Wavenet-D">Hi <emphasis level="strong">there</emphasis> <break time="2s"/> now</voice></speak>',
        ),
    ],
)
def test_combined_rules(processor, input_text, expected):
    assert processor.to_ssml(input_text) == expected
