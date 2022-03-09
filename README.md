# Decision Support Tool


1. Install `pre-commit` ([Docs](https://pre-commit.com/), [GitHub](https://github.com/pre-commit/pre-commit)) tool to simplify commit review tasks

    Make sure `pip` [(Linux, MacOS, Windows)](https://pip.pypa.io/en/stable/installation/#installation) is installed

    ```
    pip install pre-commit
    pre-commit install
    ```

    >Supported Hooks: [check-jsonschema](https://github.com/sirosen/check-jsonschema) (ex: --schemafile)
    >- A pre-commit hook for checking files against a JSONSchema ([learn](https://json-schema.org/learn))

    To run `pre-commit` without making a commit, run

    ```
    pre-commit run --all-files
    ```

2. In JupyterHub ([Installing Jupyter](https://jupyter.org/install)), edit the `decision-support-tool.ipynb` file as you wish

3. Edit `CHANGELOG.md` accordingly to indicate what you've changed

4. Add changes to git staging env ([git add options](https://git-scm.com/docs/git-add#Documentation/git-add.txt--A))

    ```
    # Add all modified files
    git add -A

    # Or add only one file
    git add ./decision-support-tool.ipynb
    ```

5. Commit changes

    ```
    git commit -m "changed something in the notebook"
    ```

    Runs `pre-commit` checks locally.

6. Tag version ([Lightweight Tags](https://git-scm.com/book/en/v2/Git-Basics-Tagging#:~:text=the%20commit%20information.-,Lightweight%20Tags,-Another%20way%20to))


    Listing the existing tags in Git (with optional -l or --list)
    ```
    git tag
    ```
    Add same tag name as in the file ./CHANGELOG.md
    ```
    git tag <tag_name>

    git push origin <tag_name>
    ```

    This will trigger a GitHub Action which builds and push Docker image to https://hub.docker.com/r/matprov/building-dst.

7. Verify that the container image is at https://hub.docker.com/r/matprov/building-dst/tags

8. `Test the  w image locally`

    To build the container with [docker (Linux, MacOS, Windows)](https://docs.docker.com/get-docker/) locally (ex: replace YOUR_VERSION_TAG by 0.1.7)

    ```bash
    docker build -t matprov/building-dst:YOUR_VERSION_TAG .
    # Or build locally
    docker build -t TAG_NAME .
    ```

    Note that this local container tag will be retrieved instead of the remote image.<br>
    This is good for debugging purposes. However, do not push this container to the repo, as it the job of the GitHub Action.

    To run the container:

    ```bash
    docker run -p 5006:5006 -e BOKEH_ALLOW_WS_ORIGIN=127.0.0.1:5006 matprov/building-dst:YOUR_VERSION_TAG
    # Or from a local image
    docker run -p 5006:5006 -e BOKEH_ALLOW_WS_ORIGIN=127.0.0.1:5006 TAG_NAME
    ```

    In your browser, go to http://127.0.0.1:5006/building-dst/decision-support-tool

9. If the app works as you want, this container version is ready to be deployed in the staging stack

