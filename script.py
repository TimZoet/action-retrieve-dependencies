import argparse
from conan.api.conan_api import ConanAPI
from conans.model.requires import Requirement
import os
import subprocess

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--conanfile", required=True)
    parser.add_argument("--profile", required=True)
    parser.add_argument("--directory", required=True)
    args = parser.parse_args()

    visited = []

    def callback(require: Requirement):
        if require.ref.user != "timzoet":
            return
        if require.ref.name in visited:
            return
        visited.append(require.ref.name)
        
        path = os.path.join(args.directory, require.ref.name)
        subprocess.run([
            "git", "clone", "--depth", "1",
            "-b", require.ref.channel,
            "--recurse-submodules",
            f"https://github.com/TimZoet/{require.ref.name}.git",
            path
        ], check=True)
        subprocess.run([
            "conan", "export",
            "--user", require.ref.user,
            "--channel", require.ref.channel,
            path
        ], check=True)

    api = ConanAPI()
    profile = api.profiles.get_profile([args.profile])
    deps_graph = api.graph.load_graph_consumer(args.conanfile, None, None,
                                               None, None,
                                               profile, profile, None,
                                               [], [], False, False,
                                               callback)
