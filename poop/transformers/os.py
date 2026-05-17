from poop.types.os import OS, Env, Process

NAMESPACE: dict[str, object] = {
    "os": OS,
    "process": Process,
    "env": Env,
}
