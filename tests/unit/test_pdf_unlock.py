
from doc2md.utils.pdf_unlock import cleanup_temp_pdf, is_encrypted, try_decrypt
from tests.conftest import FIXTURES


def test_is_encrypted_true_on_locked_pdf() -> None:
    assert is_encrypted(FIXTURES / "sample_locked.pdf") is True


def test_is_encrypted_false_on_plain_pdf() -> None:
    assert is_encrypted(FIXTURES / "sample_digital.pdf") is False


def test_try_decrypt_returns_same_path_on_plain_pdf() -> None:
    path = FIXTURES / "sample_digital.pdf"

    assert try_decrypt(path, None) == path


def test_try_decrypt_returns_temp_path_on_locked_pdf_with_correct_password() -> None:
    decrypted_path = try_decrypt(FIXTURES / "sample_locked.pdf", "test123")

    try:
        assert decrypted_path != FIXTURES / "sample_locked.pdf"
        assert decrypted_path.exists()
        assert is_encrypted(decrypted_path) is False
    finally:
        cleanup_temp_pdf(decrypted_path)

