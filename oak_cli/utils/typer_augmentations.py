# Based on: https://github.com/tiangolo/typer/issues/132
import re

import typer


def typer_help_text(subject: str) -> str:
    return f"Command for {subject} related activities."


class AliasGroup(typer.core.TyperGroup):

    _CMD_SPLIT_P = r"[,| ?\/]"  # Adds other delimiters inside the [ ]

    def get_command(self, ctx, cmd_name):
        cmd_name = self._group_cmd_name(cmd_name)
        return super().get_command(ctx, cmd_name)

    def _group_cmd_name(self, default_name):
        for cmd in self.commands.values():
            if cmd.name and default_name in re.split(self._CMD_SPLIT_P, cmd.name):
                return cmd.name
        return default_name
