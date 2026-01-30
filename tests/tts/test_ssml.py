import pytest

from slide_voice_app.tts.ssml import SSMLProcessor


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
            "[en-US-Wavenet-D] _Hi_ there ..",
            '<speak><voice name="en-US-Wavenet-D"> <emphasis level="strong">Hi</emphasis> there <break time="2s"/></voice></speak>',
        ),
        # Escape XML special characters in content
        (
            "R&D Department <sales@example.com>",
            "<speak>R&amp;D Department &lt;sales@example.com&gt;</speak>",
        ),
        # Escape quotes in voice name
        (
            '[en-US-Wavenet-D" malicious]Hello there.',
            '<speak><voice name="en-US-Wavenet-D&quot; malicious">Hello there.</voice></speak>',
        ),
    ],
)
def test_combined_rules(input_text, expected):
    assert SSMLProcessor.to_ssml(input_text) == expected
