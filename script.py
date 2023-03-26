import argparse
from conan.api.conan_api import ConanAPI
import os
import subprocess

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--conanfile", required=True)
    parser.add_argument("--profile", required=True)
    parser.add_argument("--directory", required=True)
    args = parser.parse_args()

    api = ConanAPI()
    profile = api.profiles.get_profile([args.profile])
    deps_graph = api.graph.load_graph_consumer(args.conanfile, None, None,
                                               None, None,
                                               profile, profile, None,
                                               [], [], [])
    
    for node in deps_graph.nodes[1:]:
        if node.conanfile.user != "timzoet":
            continue
        
        path = os.path.join(args.directory, node.conanfile.name)
        
        subprocess.run([
            "git", "clone", "--depth", "1",
            "-b", node.conanfile.channel,
            f"https://github.com/TimZoet/{node.conanfile.name}.git",
            path
        ], check=True)

        subprocess.run([
            "conan", "export",
            "--user", node.conanfile.user,
            "--channel", node.conanfile.channel,
            path
        ], check=True)
