Releasing a new version
=======================

We will use the `v0.15.8` release [#202](https://github.com/fedora-iot/greenboot/pull/202) as an example of how to release a new
greenboot version:

* Fork the repo and create a new branch for the new release:

    ```bash
    gh repo fork fedora-iot/greenboot --clone --remote
    git pull upstream main
    git checkout -b prepare-v0.15.8
    ```

* Update the `greenboot.spec` file and set the new version: `rpmdev-bumpspec -n 0.15.8 greenboot.spec`
* Update anything required for the new RPM
* Update the changelog section of the spec file
* Commit all the changes and create a PR (see #738 with all the changes described
above):

    ```bash
    git add greenboot.spec # add anything else needed
    git commit -s -m "chore: bump for 0.15.8 release" -m "Prepare for the 0.15.8 release."
    gh pr create
    ```

* Once all the tests pass and the PR is merged, tag and sign the release:

    ```bash
    git tag -a -s v0.15.8
    git push upstream v0.15.8
    ```

* Using the webui, open the [Releases](https://github.com/fedora-iot/greenboot/releases)
page and click the "Draft a new release" button in the middle of the page. From
there you can choose the `v0.15.8` tag you created in the previous step.
  * Use the version as the "Release title" and keep the format i.e. "v0.15.8".
  * In the description add in any release notes or click "Generate release notes".
  When satisfied, click the "Save draft" or "Publish release" button at the bottom of the page.
