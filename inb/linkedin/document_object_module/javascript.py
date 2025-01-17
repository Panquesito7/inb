# pylint: disable=missing-module-docstring

# Copyright 2021, joshiayus Inc.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
#     * Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above
# copyright notice, this list of conditions and the following disclaimer
# in the documentation and/or other materials provided with the
# distribution.
#     * Neither the name of joshiayus Inc. nor the names of its
# contributors may be used to endorse or promote products derived from
# this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from __future__ import annotations

import time

from linkedin import driver

_GET_PAGE_Y_OFFSET_SCRIPT = (
    'return (window.pageYOffset !== undefined)'
    '  ? window.pageYOffset'
    '  : (document.documentElement || document.body.parentNode || document.body);'  # pylint: disable=line-too-long
)

_SCROLL_TO_BOTTOM_SCRIPT = (
    'var scrollingElement = (document.scrollingElement || document.body);'
    'scrollingElement.scrollTop = scrollingElement.scrollHeight;')


class JS:  # pylint: disable=missing-module-docstring
  """Utility JavaScript scripts to use at runtime."""

  @staticmethod
  def load_page() -> None:
    """Loads the page the bot is currently at by scrolling it down."""
    old_page_offset = new_page_offset = driver.GetGlobalChromeDriverInstance(
    ).execute_script(_GET_PAGE_Y_OFFSET_SCRIPT)
    while old_page_offset == new_page_offset:
      driver.GetGlobalChromeDriverInstance().execute_script(
          _SCROLL_TO_BOTTOM_SCRIPT)
      time.sleep(1)
      new_page_offset = driver.GetGlobalChromeDriverInstance().execute_script(
          _GET_PAGE_Y_OFFSET_SCRIPT)
