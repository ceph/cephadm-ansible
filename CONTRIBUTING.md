# Contributing to cephadm-ansible

1. Follow the [commit guidelines](#commit-guidelines)

## Commit guidelines

- All commits should have a subject and a body
- The commit subject should briefly describe the change introduced by the
  commit
- The commit body should describe the problem addressed by the commit and the
  solution chosen
  - What was the problem and solution? Why that solution? Were there alternative ideas?
- Wrap commit subjects and bodies to 80 characters
- Sign-off your commits
- Add a best-effort scope designation to commit subjects. This could be a
  directory name, file name, or the name of a logical grouping of code.
  Examples:
  - library: add a placeholder module for the validate action plugin
  - site.yml: combine validate play with fact gathering play
- Commits linked with an issue should be tracked with a string of the following form:
  - Fixes: #2653

[Suggested reading.](https://chris.beams.io/posts/git-commit/)

## Pull requests

### Jenkins CI

We use Jenkins to run various tests on each pull request.

If you prefer not to run a build for a particular pull request, because for
example you are just changing the `README`, add the text `[skip ci]` to the PR
title.

### Merging strategy

Merging PR is controlled by [mergify](https://mergify.io/) by the following
rules:

- at least one approval from a maintainer
- SUCCESS from every Jenkins status reported by the cephadm-ansible PR
  pipeline (`Testing: flake8`, `Testing: mypy`, `Testing: unittests`,
  `Testing: el9-functional`, `Testing: el10-functional`)

If your work is not ready for review and merging, request the `DNM` (**D**o
**N**ot **M**erge) label via a comment or the title of your PR. This will
prevent the engine from merging your pull request.

### Backports (maintainers only)

If you want to backport your work from `main` to a stable branch, contact a
maintainer and ask them to set the backport label on your PR. When the PR from
`main` is merged, a backport PR will be created by mergify. If there is a
cherry-pick conflict, you must resolve it by pulling the branch.

**NEVER** push directly into a stable branch, **unless** the code from main has
diverged so much that the files don't exist in the stable branch.  If that
happens, inform the maintainers of the reasons why you pushed directly into a
stable branch, if the reason is invalid, maintainers will immediatly close your
pull request.

### Keep your branch up-to-date

Sometimes, a pull request can be subject to long discussion, reviews and
comments. In the meantime, `main` moves forward. In these circumstances, keep
your branch rebased on `main` regularly to avoid merge conflicts. A rebased
branch is easier to merge than a branch that has fallen out of sync with `main`
and has not been rebased on `main`.

### Organize your commits

Do not split your commits unecessarily. Squash or amend commits that have
titles like "I'm addressing reviewer's comments".

On the other hand, split your commits when it is smarter to do so. If you are
modifying several distinct parts of `cephadm-ansible` or you are pushing a
large patch, it might be better to split your large commit into multiple
smaller commits so that others can more easily understand your work.

Some recommendations:

- one fix = one commit,
- do not mix multiple topics in a single commit
- when your PR contains many commits that are not related to one another,
  split those commits across several PRs

If your work has been broken up into a set of sequential changes and each
commit passes the tests individually, then that's fine. Any commits that fix
typos or address problems introduced by other commits in the same PR should be
squashed before merging.

If you are new to Git, these links might help:

- [https://git-scm.com/book/en/v2/Git-Tools-Rewriting-History](https://git-scm.com/book/en/v2/Git-Tools-Rewriting-History)
- [http://gitready.com/advanced/2009/02/10/squashing-commits-with-rebase.html](http://gitready.com/advanced/2009/02/10/squashing-commits-with-rebase.html)
