# Decision Support Tool


1. Install `pre-commit` tool to simplify commit review tasks

    ```
    pip install pre-commit
    pre-commit install
    ```

    To run `pre-commit` without making a commit, run `pre-commit run --all-files`.

2. In JupyterHub, edit the `decision-support-tool.ipynb`file as you wish

3. Edit `CHANGELOG.md` accordingly to indicate what you've changed

4. Add changes to git staging env

    ```
    git add -A
    ```

5. Commit changes

    ```
    git commit -m "changed something in the notebook"
    ```
    
    Runs `pre-commit` checks locally.

6. Tag version

    ```
    git tag <tag_name>
    git push origin <tag_name>
    ```

    This will trigger a GitHub Action which builds and push Docker image to https://hub.docker.com/r/crimca/decision-support-tool.

7. Verify that the container image is at https://hub.docker.com/r/crimca/decision-support-tool/tags

8. Test the image locally

    ## To build the container locally:

    ```
    docker build -t crimca/decision-support-tool:YOUR_VERSION_TAG .
    ```

    Note that this local container tag will be retrieved instead of the remote image.<br>
    This is good for debugging purposes. However, do not push this container to the repo, as it the job of the GitHub Action.

    ## To run the container:

    ```
    docker run -p 5006:5006 -e BOKEH_ALLOW_WS_ORIGIN=127.0.0.1:5006 crimca/decision-support-tool:YOUR_VERSION_TAG
    ```

    In your browser, go to http://127.0.0.1:5006/building-dst/decision-support-tool

9. If the app works as you want, this container version is ready to be deployed in the staging stack
