# GitHub Action - retrieve-dependencies

Retrieve Conan dependencies of the package that is currently being built from GitHub, and export them to the local Conan cache.

```yml
- uses: TimZoet/action-retrieve-dependencies@trunk
  with:
    # Path to conanfile of package whose dependencies will be retrieved.
    # default: ''
    conanfile: ''

    # Path to profile with which required dependencies are determined.
    # default: ''
    profile: ''

    # Path to directory in which all dependencies will be stored.
    # default: ''
    directory: ''
```
