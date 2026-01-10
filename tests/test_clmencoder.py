import pytest
from pytest_mock import MockerFixture

from clm_core.encoder import CLMEncoder
from clm_core.config.schemas import CLMConfig
from clm_core.core.text_classifier import DataTypes
from clm_core.types import CLMOutput


@pytest.fixture
def cfg(mocker: MockerFixture) -> CLMConfig:
    # Build a CLMConfig but stub out heavy resources
    # Load a real spaCy model for tests since it's needed for matchers
    import spacy
    try:
        real_nlp = spacy.load("en_core_web_sm")
    except OSError:
        pytest.skip("spaCy model en_core_web_sm not available")

    mocker.patch("spacy.load", return_value=real_nlp)
    config = CLMConfig()
    # Vocab, rules are computed_fields; ensure they are usable in constructor calls
    # They can remain as the default maps unless needed to be mocked
    return config


def test_encode_structured_data_routes_to_dsencoder(mocker: MockerFixture, cfg: CLMConfig):
    encoder = CLMEncoder(cfg=cfg)

    # Force classification to STRUCTURED_DATA
    mocker.patch.object(encoder._classifier, "classifier", return_value=DataTypes.STRUCTURED_DATA)

    mocked_output = CLMOutput(
        original={"id": "1"},
        component="ds_compression",
        compressed="[ID:1]",
        metadata={}
    )
    mocked_ds_encode = mocker.patch(
        "clm_core.components.ds_compression.DSEncoder.encode",
        return_value=mocked_output
    )

    input_data = [{"id": "1", "name": "A"}]
    result = encoder.encode(input_data)

    mocked_ds_encode.assert_called_once_with(input_data)
    assert isinstance(result, CLMOutput)
    assert result is mocked_output


def test_encode_transcript_routes_with_metadata_and_verbose(mocker: MockerFixture, cfg: CLMConfig):
    encoder = CLMEncoder(cfg=cfg)

    mocker.patch.object(encoder._classifier, "classifier", return_value=DataTypes.TRANSCRIPT)

    mocked_output = CLMOutput(
        original="Agent: Hello\nCustomer: Hi",
        component="TRANSCRIPT",
        compressed="[CALL:SUPPORT]",
        metadata={}
    )
    mocked_ts_encode = mocker.patch(
        "clm_core.components.transcript.encoder.TranscriptEncoder.encode",
        return_value=mocked_output
    )

    transcript_text = "Agent: Hello\nCustomer: Hi"
    metadata = {"call_id": "ABC"}
    result = encoder.encode(transcript_text, verbose=True, metadata=metadata)

    mocked_ts_encode.assert_called_once_with(transcript=transcript_text, verbose=True, metadata=metadata)
    assert isinstance(result, CLMOutput)
    assert result is mocked_output


def test_encode_system_prompt_routes_to_syspromptencoder(mocker: MockerFixture, cfg: CLMConfig):
    encoder = CLMEncoder(cfg=cfg)

    mocker.patch.object(encoder._classifier, "classifier", return_value=DataTypes.SYSTEM_PROMPT)

    mocked_output = CLMOutput(
        original="Your task is to summarize the following text.",
        component="SYSTEM_PROMPT",
        compressed="[INTENT:SUMMARIZE]",
        metadata={}
    )
    mocked_sys_compress = mocker.patch(
        "clm_core.components.sys_prompt.encoder.SysPromptEncoder.compress",
        return_value=mocked_output
    )

    prompt = "Your task is to summarize the following text."
    result = encoder.encode(prompt, verbose=False)

    mocked_sys_compress.assert_called_once_with(prompt, False)
    assert isinstance(result, CLMOutput)
    assert result is mocked_output


def test_encode_unknown_type_returns_none(mocker: MockerFixture, cfg: CLMConfig, capsys):
    encoder = CLMEncoder(cfg=cfg)

    mocker.patch.object(encoder._classifier, "classifier", return_value=DataTypes.UNK)

    result = encoder.encode("???", verbose=True)
    captured = capsys.readouterr()

    assert result is None
    assert "Unknown Data Type. Can't compress" in captured.out


def test_encode_unsupported_input_types_safe_handling(mocker: MockerFixture, cfg: CLMConfig):
    encoder = CLMEncoder(cfg=cfg)

    mocker.patch.object(encoder._classifier, "classifier", return_value=DataTypes.UNK)

    # Unsupported types like integers
    result = encoder.encode(12345)
    assert result is None

    class Obj:
        pass

    result_obj = encoder.encode(Obj())
    assert result_obj is None


def test_encode_transcript_handles_none_metadata(mocker: MockerFixture, cfg: CLMConfig):
    encoder = CLMEncoder(cfg=cfg)

    mocker.patch.object(encoder._classifier, "classifier", return_value=DataTypes.TRANSCRIPT)

    mocked_output = CLMOutput(
        original="Agent: Hi\nCustomer: Hello",
        component="TRANSCRIPT",
        compressed="[CALL:SUPPORT]",
        metadata={}
    )
    mocked_ts_encode = mocker.patch(
        "clm_core.components.transcript.encoder.TranscriptEncoder.encode",
        return_value=mocked_output
    )

    transcript_text = "Agent: Hi\nCustomer: Hello"
    result = encoder.encode(transcript_text, metadata=None)

    mocked_ts_encode.assert_called_once_with(transcript=transcript_text, verbose=False, metadata=None)
    assert isinstance(result, CLMOutput)


def test_constructor_uses_clmconfig_dependencies(mocker: MockerFixture, cfg: CLMConfig):
    # Ensure that constructing CLMEncoder pulls from cfg and initializes dependencies
    encoder = CLMEncoder(cfg=cfg)

    assert encoder._nlp is cfg.nlp_model
    # Ensure component encoders are instantiated
    assert encoder._ds_encoder is not None
    assert encoder._ts_encoder is not None
    assert encoder._sys_prompt_encoder is not None
    # Ensure classifier is instantiated
    assert encoder._classifier is not None


def test_encode_propagates_verbose_flag_to_encoder(mocker: MockerFixture, cfg: CLMConfig):
    encoder = CLMEncoder(cfg=cfg)

    # Test for transcript path with verbose True propagation
    mocker.patch.object(encoder._classifier, "classifier", return_value=DataTypes.TRANSCRIPT)
    mocked_ts_encode = mocker.patch(
        "clm_core.components.transcript.encoder.TranscriptEncoder.encode",
        return_value=CLMOutput(
            original="Agent: Hello\nCustomer: Hi",
            component="TRANSCRIPT",
            compressed="[CALL:SUPPORT]",
            metadata={}
        )
    )
    transcript_text = "Agent: Hello\nCustomer: Hi"
    _ = encoder.encode(transcript_text, verbose=True, metadata={})
    mocked_ts_encode.assert_called_once()
    args, kwargs = mocked_ts_encode.call_args
    assert kwargs.get("verbose") is True
