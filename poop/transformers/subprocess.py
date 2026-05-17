from poop.types.subprocess import CompletedProcess, Popen, Subprocess

NAMESPACE: dict[str, object] = {
    "subprocess": Subprocess,
    "Popen": Popen,
    "CompletedProcess": CompletedProcess,
}
