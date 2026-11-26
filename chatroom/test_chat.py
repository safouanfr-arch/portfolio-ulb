"""Loopback integration tests. Run after building both C programs."""

from contextlib import ExitStack
from pathlib import Path
import re
import select
import socket
import subprocess
import unittest


HERE = Path(__file__).resolve().parent


class ChatTests(unittest.TestCase):
    def setUp(self):
        with socket.socket() as probe:
            probe.bind(("127.0.0.1", 0))
            self.address = probe.getsockname()
        self.server = subprocess.Popen(
            [HERE / "chat-server", str(self.address[1])],
            stdout=subprocess.PIPE,
            text=True,
        )
        self.addCleanup(self.stop_server)
        self.assertTrue(select.select([self.server.stdout], [], [], 5)[0])
        self.assertIn("listening", self.server.stdout.readline())

    def stop_server(self):
        self.server.terminate()
        try:
            self.server.wait(timeout=5)
        except subprocess.TimeoutExpired:
            self.server.kill()
            self.server.wait()
        self.server.stdout.close()

    def attach(self, clients, name):
        sock = clients.enter_context(socket.create_connection(self.address, timeout=3))
        stream = clients.enter_context(sock.makefile("rb"))
        username = name.encode().ljust(32, b"\0")
        sock.sendall(username[:11])
        sock.sendall(username[11:])
        self.assertEqual(stream.readline(), b"Welcome to discULB.\n")
        return sock, stream

    def test_tcp_framing_and_client_round_trip(self):
        with ExitStack() as clients:
            observer, messages = self.attach(clients, "Observer")
            sender, _ = self.attach(clients, "Sender")
            self.assertEqual(messages.readline(), b"Sender joined the chat.\n")
            sender.sendall(b"first ")
            self.assertFalse(select.select([observer], [], [], 0.1)[0])
            sender.sendall(b"line\nsecond line\n")
            self.assertEqual(messages.readline(), b"first line\n")
            self.assertEqual(messages.readline(), b"second line\n")

            subprocess.run(
                [HERE / "chat-client", "Alice", *map(str, self.address)],
                input="hello\nexit\n",
                text=True,
                capture_output=True,
                check=True,
                timeout=5,
            )
            self.assertEqual(messages.readline(), b"Alice joined the chat.\n")
            self.assertRegex(messages.readline(), re.compile(rb"^\[\d\d:\d\d:\d\d\] Alice: hello\n$"))
            self.assertEqual(messages.readline(), b"Alice left the chat.\n")

    def test_capacity(self):
        with ExitStack() as clients:
            for i in range(4):
                self.attach(clients, f"Client {i}")
            extra = clients.enter_context(socket.create_connection(self.address, timeout=3))
            stream = clients.enter_context(extra.makefile("rb"))
            self.assertIn(b"chat is full", stream.readline())


if __name__ == "__main__":
    unittest.main()
