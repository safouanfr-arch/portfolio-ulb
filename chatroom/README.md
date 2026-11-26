# discULB Chatroom

A terminal-based group chat written in C for the ULB INFO-F-201 operating systems course. Up to four clients can join a local TCP server, send timestamped messages, and see who joins or leaves.

## Run

On Linux, macOS, or WSL with a C compiler and Make:

```sh
make
./chat-server 8080
```

In two other terminals:

```sh
./chat-client Alice 127.0.0.1 8080
./chat-client Bob 127.0.0.1 8080
```

Type a message and press Enter. Type `exit` to disconnect. Run `python3 test_chat.py` after building to check the server and client together on loopback.

## Implementation

The server keeps one POSIX thread per client and uses a mutex to protect the client list. It broadcasts a message to the other participants. The client uses `poll` to listen to the socket and stdin. The protocol starts with the original 32-byte, NUL-padded username, followed by newline-terminated messages. The server listens on loopback for a local demo.

## Credits

ULB course submission by Safouan Tassi and Victor Burton. This revision combines the behavior of the submitted chat with the fixes from the later local copy, including the username handling, and adds bounded message input, complete socket writes, and an integration test.

The original implementation was adapted from a [chatroom tutorial](https://youtu.be/fNerEo6Lstw). The Apache 2.0 license carried with that source is included in [LICENSE](LICENSE).
