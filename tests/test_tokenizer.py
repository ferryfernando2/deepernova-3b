from src.tokenizer import SimpleTokenizer


def test_tokenizer_roundtrip():
    texts = ["Hello world", "Hello AI world"]
    tok = SimpleTokenizer()
    tok.build_vocab(texts, vocab_size=10)
    encoded = tok.encode("Hello world")
    decoded = tok.decode(encoded)
    assert "hello" in decoded
    assert "world" in decoded
