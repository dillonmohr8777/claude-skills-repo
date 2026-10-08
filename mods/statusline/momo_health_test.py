import io
import json
import unittest
from momo_health import READY_URL, readiness


class Response(io.BytesIO):
    status = 200


class ReadinessTests(unittest.TestCase):
    def test_exact_momo_readiness_route(self):
        def opener(url, timeout):
            self.assertEqual(url, "http://127.0.0.1:2026/health/ready")
            self.assertEqual(timeout, 4)
            return Response(json.dumps({"status": "ready", "service": "deer-flow-gateway"}).encode())
        self.assertEqual(readiness(opener), "up")
        self.assertNotIn("3434", READY_URL)

    def test_rockbot_or_login_payload_never_counts_as_momo(self):
        for data in [b'{"status":"ready","service":"rockbot"}', b'<html>Sign in</html>', b'{"status":"unready","service":"deer-flow-gateway"}']:
            self.assertEqual(readiness(lambda *args, **kwargs: Response(data)), "down")

    def test_http_failure_and_unreachable_fail_closed(self):
        response = Response(b'{"status":"ready","service":"deer-flow-gateway"}')
        response.status = 503
        self.assertEqual(readiness(lambda *args, **kwargs: response), "down")
        def unavailable(*args, **kwargs):
            raise OSError("offline")
        self.assertEqual(readiness(unavailable), "down")


if __name__ == "__main__":
    unittest.main()
