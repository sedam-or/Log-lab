import unittest

from loglab.security import hash_password, pseudonym, verify_password


class SecurityTests(unittest.TestCase):
    def test_scrypt_password_hash_is_salted_and_verified(self):
        first = hash_password("a-long-fictitious-password")
        second = hash_password("a-long-fictitious-password")
        self.assertTrue(first.startswith("scrypt$16384$8$1$"))
        self.assertNotEqual(first, second)
        self.assertTrue(verify_password("a-long-fictitious-password", first))
        self.assertFalse(verify_password("incorrect-password", first))
        self.assertFalse(verify_password("a-long-fictitious-password", "scrypt$999999999$8$1$aa$00"))

    def test_pseudonyms_are_stable_and_namespaced(self):
        key = b"k" * 32
        self.assertEqual(pseudonym(key, "account", "Alice"), pseudonym(key, "account", " alice "))
        self.assertNotEqual(pseudonym(key, "account", "alice"), pseudonym(key, "client", "alice"))


if __name__ == "__main__":
    unittest.main()
