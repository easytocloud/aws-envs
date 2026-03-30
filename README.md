# aws-envs

Manage multiple AWS organizations cleanly by organizing credentials into separate **environments**.

## Problem Statement

Managing AWS profiles across multiple organizations is risky and confusing:

- Which profile belongs to which organization?
- Easy to run a command against the wrong account
- All credentials in a single `~/.aws/credentials` file is hard to reason about

## Solution: Environments

`aws-envs` introduces the concept of an **environment** — a named directory that holds the `config` and `credentials` files for one AWS organization. Only one environment is active at a time.

```
~/.aws/aws-envs/
  my-org-1/
    config
    credentials
  my-org-2/
    config
    credentials
```

`~/.aws/config` and `~/.aws/credentials` are symlinks pointing to the active environment's files. Switching environments updates those symlinks (or the `AWS_CONFIG_FILE` / `AWS_SHARED_CREDENTIALS_FILE` environment variables).

Within an environment you still use standard AWS **profiles** — `ase` selects the environment, `asp` selects the profile within it.

## Key Concepts

| Term | Meaning |
|------|---------|
| **environment** | A directory under `~/.aws/aws-envs/`, typically one per AWS organization |
| **profile** | A named set of credentials/config within an environment (standard AWS concept) |
| `ase` | Shell function to **switch environments** (sets `AWS_ENV`, updates symlinks/vars) |
| `asp` | Shell function to **switch profiles** within the active environment (sets `AWS_PROFILE`) |

## Usage

```zsh
# Switch to an environment
ase my-org-1

# Or pick interactively
ase
# 1 my-org-1    2 my-org-2
# Enter environment number [1-2]> _

# Switch profile within the active environment
asp dev-account

# Or pick interactively
asp
# 1 dev-account    2 prod-account    3 sandbox
# Enter profile number [1-3]> _

# Create a new empty environment
ase --add new-env
```

The `ase` and `asp` shell functions are provided by the [oh-my-easytocloud](https://github.com/easytocloud/oh-my-easytocloud) plugin for oh-my-zsh. See that repo for installation and prompt integration.

## Initial Setup

If you currently have a standard `~/.aws/credentials` and `~/.aws/config` (a single-environment setup), run the one-time migration tool to convert it into an `aws-envs` structure:

```shell
uvx aws-envs-setup
```

No installation required — `uvx` runs it directly. The tool will:

1. Ask you to name your first environment (e.g. the AWS organization it represents)
2. Move your existing `~/.aws/config` and `~/.aws/credentials` into `~/.aws/aws-envs/<name>/`
3. Create symlinks from `~/.aws/config` and `~/.aws/credentials` back to the active environment
4. Write `~/.awsdefaultenv` so your shell picks up the right environment on login

After setup, install [oh-my-easytocloud](https://github.com/easytocloud/oh-my-easytocloud) to get the `ase` and `asp` shell functions.

## File Structure After Setup

```
~/.aws/
  config           -> aws-envs/my-org-1/config   (symlink)
  credentials      -> aws-envs/my-org-1/credentials (symlink)
  aws-envs/
    my-org-1/
      config
      credentials
~/.awsdefaultenv   (contains: my-org-1)
~/.awsdefaultprofile (optional, contains default profile name)
```

## Adding More Environments

```zsh
ase --add my-org-2
aws configure --profile my-first-account
```

## Tips

- Use `aws configure` as normal — it writes to whichever environment is currently active
- `aws sso login` works per-environment; CLI v2 SSO is fully supported
- Consider [ssostart](https://github.com/easytocloud/ssostart) for environment-aware SSO login (`brew install easytocloud/tap/ssostart`)
- A prompt that shows the active environment and profile prevents costly mistakes — [oh-my-easytocloud](https://github.com/easytocloud/oh-my-easytocloud) provides this out of the box

## Legacy

This project supersedes [aws-profile-organizer](https://github.com/easytocloud/aws-profile-organizer). The underlying `~/.aws/aws-envs/` directory structure is identical — no migration needed if you used `aws-profile-organizer` before.

## License

[MIT License](LICENSE.md)
