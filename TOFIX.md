# TOFIX

Findings from a code scan on 2026-10-04.

## High

- `rsconstruct.toml:1-23` - the five Python scripts in `scripts/` are checked by no processor and their imports (`azure-identity`, `azure-mgmt-resource`, `azure-core`) are declared nowhere; `ruff check --no-cache scripts` reports 31 findings (unused imports, unused variables, blind `except Exception`). Add a `pyproject.toml` declaring the azure packages (bare names) plus a `ruff` dev dependency and lockfile, add `[processor.ruff] src_dirs = ["scripts"]`, and fix the findings.
- `exercises/create_repo_and_push_code/solution.bash:5` and `:20` - the Azure DevOps PAT is read from a plain file `~/.token` and then embedded in the git remote URL, so `git remote add` writes it in clear text into `project/.git/config`. Fetch it with `pass show` at run time and pass it via a credential helper or `http.extraHeader` instead of the URL.

## Medium

- `terraform/scripts/delete_images.sh:3-14`, `terraform/scripts/get_resources.sh:2-17`, `terraform/scripts/remove_state.sh:2` - these are AWS scripts (ECR repo `trainpipe`, SQS/Batch/EFS, S3 backend `sagemaker-tf-backend`) copied from another project; nothing in this Azure repo or in `terraform/project.tf` uses them. Delete them.
- `terraform/project.tf:27-33` - `azurerm_public_ip` uses `sku = "Basic"` with `allocation_method = "Dynamic"`; Azure retired Basic-SKU public IPs on 2025-09-30, so `terraform apply` can no longer create this. Switch to `sku = "Standard"` with `allocation_method = "Static"`.
- `rsconstruct.toml:1-23` - `terraform/project.tf` is linted by nothing, and it mixes tab and two-space indentation (lines 1-18 vs 20-76), i.e. it is not `terraform fmt` clean. Add a terraform fmt/validate (or tflint) processor for `terraform/` and run `terraform fmt`.
- `scripts/cleanup-resources.py:97-98` and `:163` - a log file name is computed and the script prints "Log saved to: ..." but nothing is ever written to it. Either log to that file or drop the message.
- `scripts/delete-pipelines.py:3` and `:85-97` - the docstring promises to "delete all pipelines and their runs", but runs are only cancelled (and only in-progress ones, `:196`); the `az pipelines runs --help` call at `:88` is dead code whose result is never used, and the comment at `:93` names a different command than the one run. Fix the docstring/comment and remove the dead call.
- `scripts/cleanup-account.py:79` - `--force` ("Skip individual resource group confirmations") is parsed but never read; the per-group prompt at `:56` always runs. Implement it (as `cleanup-resources.py` does with `--skip-confirmation`) or remove it.
- `scripts/cleanup-account.py:134` and `scripts/cleanup-resources.py:165` - a blind `except Exception` prints the error and exits 0 (`cleanup-account.py`) after partial destructive work; let the exception propagate or `sys.exit(1)`.

## Low

- `scripts/cleanup-account.py` and `scripts/cleanup-resources.py` - two near-identical "delete every resource group" scripts; keep one. Likewise `ensure_devops_extension`/`configure_devops_defaults` are copy-pasted in `delete-git-repos.py:13-51`, `delete-library-items.py:12-50` and `delete-pipelines.py`; share them.
- `scripts/cleanup-resources.py:29-37` - `AzureCliCredential()` does not authenticate in its constructor, so the `except ClientAuthenticationError` fallback to `DefaultAzureCredential` can never trigger; use `ChainedTokenCredential` or just `DefaultAzureCredential`. The usage line at `:15` also names a non-existent `azure_cleanup.py`.
- `scripts/whoami.sh:2` and `scripts/azure-whoami.sh:2` - identical scripts; delete one.
- `terraform/scripts/create_role.sh:3` - a concrete subscription ID is hardcoded; take it from `az account show --query id -o tsv` or an argument.
- `exercises/create_repo_and_push_code/solution.bash:20` - the remote URL hardcodes `markveltzer/training` instead of `${ORGANIZATION}/${PROJECT}` defined at `:7-8`; and `cd project` (`:22`) refers to a directory that is not in the repo, which the exercise never explains.
- `exercises/setting_up_virtual_machine/exercise.md:12`, `:50`, `:146` - section headings are numbered "1.", "4.", "9." while the others are unnumbered; number all or none.
- `README.md:2` - the README does not list or describe any of the scripts, the terraform demo, or the exercises.
