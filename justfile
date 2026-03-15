docs:
    @echo "ℹ Building documentation... 📝"
    @uv run sphinx-build -M html docs docs/_build/ -E -a -j auto -W --keep-going

# Serve the docs locally
docs-serve:
    @echo "ℹ Starting documentation server... 📚"
    @uv run sphinx-autobuild docs docs/_build/ -j auto --watch src --watch docs --watch README.rst --port 8002
