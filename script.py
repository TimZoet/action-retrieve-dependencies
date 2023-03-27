import argparse
import os
import subprocess

from conan.api.conan_api import ConanAPI
from conans.client.graph.graph_error import GraphError
from conans.model.requires import Requirement

def export(directory: str, require: Requirement):
    path = os.path.join(directory, require.ref.name)

    # Retrieve source from GitHub.
    subprocess.run([
        "git", "clone", "--depth", "1",
        "-b", require.ref.channel,
        f"https://github.com/TimZoet/{require.ref.name}.git",
        path
    ], check=True)

    # Some temp fixes because we cannot handle submodules referenced through SSH.
    if require.ref.name == "bettertest":
        subprocess.run(["git", "submodule", "set-url", "--", "modules/bettertest_alexandria", "https://github.com/TimZoet/bettertest-alexandria-module.git"], cwd=path, check=True)
        subprocess.run(["git", "submodule", "set-url", "--", "modules/bettertest_json", "https://github.com/TimZoet/bettertest-json-module.git"], cwd=path, check=True)
        subprocess.run(["git", "submodule", "set-url", "--", "modules/bettertest_xml", "https://github.com/TimZoet/bettertest-xml-module.git"], cwd=path, check=True)
        subprocess.run(["git", "submodule", "update", "--init"], cwd=path, check=True)

    # Export to local cache.
    subprocess.run([
        "conan", "export",
        "--user", require.ref.user,
        "--channel", require.ref.channel,
        path
    ], check=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--conanfile", required=True)
    parser.add_argument("--profile", required=True)
    parser.add_argument("--directory", required=True)
    args = parser.parse_args()

    api = ConanAPI()
    profile = api.profiles.get_profile([args.profile])
    remotes = api.remotes.list()

    # Iteratively discover missing pacakges by trying to construct the dependency graph.
    while True:
        # Try to construct dependency graph.
        deps_graph = api.graph.load_graph_consumer(args.conanfile, None, None,
                                                   None, None,
                                                   profile, profile, None,
                                                   remotes, [], False, False)
        
        # No error means all good, all packages found.
        if not deps_graph.error:
            break
        
        # Unexpected error or missing package from some other weirdo.
        if deps_graph.error.kind != GraphError.MISSING_RECIPE or deps_graph.error.require.ref.user != "timzoet":
            raise RuntimeError(f"Unexpected error while traversing graph: {deps_graph.error}")

        # Retrieve and export our own package.
        export(args.directory, deps_graph.error.require)
